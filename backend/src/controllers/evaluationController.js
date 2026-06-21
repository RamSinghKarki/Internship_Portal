const prisma = require('../config/database');

const createOrUpdate = async (req, res) => {
  try {
    const {
      enrollmentId, technicalScore, communicationScore, teamworkScore,
      punctualityScore, overallScore, feedback, strengths, improvements, grade, isRecommended,
    } = req.body;

    let canAccess = false;
    if (req.user.role === 'ADMIN') {
      canAccess = true;
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

    const data = {
      technicalScore: technicalScore ? parseFloat(technicalScore) : null,
      communicationScore: communicationScore ? parseFloat(communicationScore) : null,
      teamworkScore: teamworkScore ? parseFloat(teamworkScore) : null,
      punctualityScore: punctualityScore ? parseFloat(punctualityScore) : null,
      overallScore: overallScore ? parseFloat(overallScore) : null,
      feedback, strengths, improvements, grade,
      isRecommended: isRecommended !== undefined ? Boolean(isRecommended) : null,
    };

    const evaluation = await prisma.evaluation.upsert({
      where: { enrollmentId },
      update: { ...data, updatedAt: new Date() },
      create: { enrollmentId, ...data },
    });

    const enrollment = await prisma.internshipEnrollment.findUnique({
      where: { id: enrollmentId },
      include: { student: { include: { user: true } } },
    });

    await prisma.notification.create({
      data: {
        userId: enrollment.student.userId,
        title: 'Evaluation Submitted',
        message: 'Your internship evaluation has been submitted',
        type: 'SUPERVISOR_FEEDBACK',
        actionUrl: '/student/enrollments',
      },
    });

    res.json(evaluation);
  } catch (error) {
    console.error('Evaluation error:', error);
    res.status(500).json({ error: 'Failed to save evaluation' });
  }
};

const getByEnrollment = async (req, res) => {
  try {
    const { enrollmentId } = req.params;

    const evaluation = await prisma.evaluation.findUnique({
      where: { enrollmentId },
      include: {
        enrollment: {
          include: {
            student: { select: { firstName: true, lastName: true } },
            internship: { select: { title: true } },
          },
        },
      },
    });

    if (!evaluation) return res.status(404).json({ error: 'Evaluation not found' });
    res.json(evaluation);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch evaluation' });
  }
};

module.exports = { createOrUpdate, getByEnrollment };
