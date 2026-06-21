const prisma = require('../config/database');

const submitLog = async (req, res) => {
  try {
    const student = await prisma.student.findUnique({ where: { userId: req.user.id } });
    if (!student) return res.status(404).json({ error: 'Student not found' });

    const { enrollmentId, weekNumber, title, description, tasksCompleted, challenges, nextWeekPlan, hoursWorked } = req.body;

    const enrollment = await prisma.internshipEnrollment.findFirst({
      where: { id: enrollmentId, studentId: student.id, status: 'ACTIVE' },
    });
    if (!enrollment) return res.status(404).json({ error: 'Active enrollment not found' });

    const log = await prisma.progressLog.upsert({
      where: { enrollmentId_weekNumber: { enrollmentId, weekNumber: parseInt(weekNumber) } },
      update: { title, description, tasksCompleted, challenges, nextWeekPlan, hoursWorked: hoursWorked ? parseInt(hoursWorked) : null, status: 'SUBMITTED' },
      create: {
        enrollmentId, weekNumber: parseInt(weekNumber), title, description,
        tasksCompleted, challenges, nextWeekPlan,
        hoursWorked: hoursWorked ? parseInt(hoursWorked) : null,
      },
    });

    res.status(201).json(log);
  } catch (error) {
    console.error('Submit log error:', error);
    res.status(500).json({ error: 'Failed to submit progress log' });
  }
};

const getEnrollmentLogs = async (req, res) => {
  try {
    const { enrollmentId } = req.params;

    let canAccess = false;
    if (req.user.role === 'ADMIN') {
      canAccess = true;
    } else if (req.user.role === 'STUDENT') {
      const student = await prisma.student.findUnique({ where: { userId: req.user.id } });
      canAccess = !!(await prisma.internshipEnrollment.findFirst({ where: { id: enrollmentId, studentId: student?.id } }));
    } else if (req.user.role === 'COMPANY') {
      const company = await prisma.company.findUnique({ where: { userId: req.user.id } });
      canAccess = !!(await prisma.internshipEnrollment.findFirst({ where: { id: enrollmentId, internship: { companyId: company?.id } } }));
    } else if (req.user.role === 'INTERNAL_SUPERVISOR' || req.user.role === 'EXTERNAL_SUPERVISOR') {
      const supervisor = await prisma.supervisor.findUnique({ where: { userId: req.user.id } });
      canAccess = !!(await prisma.internshipEnrollment.findFirst({
        where: { id: enrollmentId, OR: [{ internalSupervisorId: supervisor?.id }, { externalSupervisorId: supervisor?.id }] },
      }));
    }

    if (!canAccess) return res.status(403).json({ error: 'Access denied' });

    const logs = await prisma.progressLog.findMany({
      where: { enrollmentId },
      include: { supervisor: { select: { firstName: true, lastName: true } } },
      orderBy: { weekNumber: 'asc' },
    });

    res.json(logs);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch progress logs' });
  }
};

const reviewLog = async (req, res) => {
  try {
    const { id } = req.params;
    const { supervisorFeedback, rating } = req.body;

    const supervisor = await prisma.supervisor.findUnique({ where: { userId: req.user.id } });
    if (!supervisor) return res.status(404).json({ error: 'Supervisor not found' });

    const log = await prisma.progressLog.findUnique({
      where: { id },
      include: { enrollment: true },
    });
    if (!log) return res.status(404).json({ error: 'Progress log not found' });

    const hasAccess =
      log.enrollment.internalSupervisorId === supervisor.id ||
      log.enrollment.externalSupervisorId === supervisor.id;
    if (!hasAccess) return res.status(403).json({ error: 'Access denied' });

    const updated = await prisma.progressLog.update({
      where: { id },
      data: {
        supervisorFeedback,
        rating: rating ? parseInt(rating) : null,
        supervisorId: supervisor.id,
        status: 'REVIEWED',
        reviewedAt: new Date(),
      },
    });

    const enrollment = await prisma.internshipEnrollment.findUnique({
      where: { id: log.enrollmentId },
      include: { student: { include: { user: true } } },
    });

    await prisma.notification.create({
      data: {
        userId: enrollment.student.userId,
        title: 'Progress Log Reviewed',
        message: `Your Week ${log.weekNumber} progress log has been reviewed`,
        type: 'SUPERVISOR_FEEDBACK',
        actionUrl: '/student/progress',
      },
    });

    res.json(updated);
  } catch (error) {
    res.status(500).json({ error: 'Failed to review progress log' });
  }
};

const getMyLogs = async (req, res) => {
  try {
    const student = await prisma.student.findUnique({ where: { userId: req.user.id } });
    if (!student) return res.status(404).json({ error: 'Student not found' });

    const { enrollmentId } = req.query;
    const logs = await prisma.progressLog.findMany({
      where: {
        enrollment: { studentId: student.id },
        ...(enrollmentId && { enrollmentId }),
      },
      include: {
        enrollment: { include: { internship: { select: { title: true } } } },
        supervisor: { select: { firstName: true, lastName: true } },
      },
      orderBy: [{ enrollment: { createdAt: 'desc' } }, { weekNumber: 'asc' }],
    });

    res.json(logs);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch logs' });
  }
};

module.exports = { submitLog, getEnrollmentLogs, reviewLog, getMyLogs };
