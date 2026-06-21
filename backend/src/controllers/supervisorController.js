const prisma = require('../config/database');

const getProfile = async (req, res) => {
  try {
    const supervisor = await prisma.supervisor.findUnique({
      where: { userId: req.user.id },
      include: {
        user: { select: { email: true, createdAt: true } },
        college: { select: { name: true } },
        company: { select: { name: true } },
      },
    });
    if (!supervisor) return res.status(404).json({ error: 'Supervisor not found' });
    res.json(supervisor);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch profile' });
  }
};

const updateProfile = async (req, res) => {
  try {
    const { firstName, lastName, phone, expertise } = req.body;
    const supervisor = await prisma.supervisor.update({
      where: { userId: req.user.id },
      data: { firstName, lastName, phone, expertise },
    });
    res.json(supervisor);
  } catch (error) {
    res.status(500).json({ error: 'Failed to update profile' });
  }
};

const getAssignedEnrollments = async (req, res) => {
  try {
    const supervisor = await prisma.supervisor.findUnique({ where: { userId: req.user.id } });
    if (!supervisor) return res.status(404).json({ error: 'Supervisor not found' });

    const { status } = req.query;
    const enrollments = await prisma.internshipEnrollment.findMany({
      where: {
        OR: [{ internalSupervisorId: supervisor.id }, { externalSupervisorId: supervisor.id }],
        ...(status && { status }),
      },
      include: {
        student: {
          include: {
            user: { select: { email: true } },
            college: { select: { name: true } },
            program: { select: { name: true } },
          },
        },
        internship: { include: { company: { select: { name: true } } } },
        _count: { select: { progressLogs: true } },
        evaluation: true,
      },
      orderBy: { createdAt: 'desc' },
    });

    res.json(enrollments);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch enrollments' });
  }
};

const getDashboardStats = async (req, res) => {
  try {
    const supervisor = await prisma.supervisor.findUnique({ where: { userId: req.user.id } });
    if (!supervisor) return res.status(404).json({ error: 'Supervisor not found' });

    const supervisorFilter = {
      OR: [{ internalSupervisorId: supervisor.id }, { externalSupervisorId: supervisor.id }],
    };

    const [assigned, active, pendingLogs] = await Promise.all([
      prisma.internshipEnrollment.count({ where: supervisorFilter }),
      prisma.internshipEnrollment.count({ where: { ...supervisorFilter, status: 'ACTIVE' } }),
      prisma.progressLog.count({
        where: { enrollment: supervisorFilter, status: 'SUBMITTED' },
      }),
    ]);

    const recentLogs = await prisma.progressLog.findMany({
      where: { enrollment: supervisorFilter, status: 'SUBMITTED' },
      include: {
        enrollment: {
          include: {
            student: { select: { firstName: true, lastName: true } },
            internship: { select: { title: true } },
          },
        },
      },
      orderBy: { submittedAt: 'desc' },
      take: 5,
    });

    res.json({ stats: { assigned, active, pendingLogs }, recentLogs });
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch dashboard stats' });
  }
};

module.exports = { getProfile, updateProfile, getAssignedEnrollments, getDashboardStats };
