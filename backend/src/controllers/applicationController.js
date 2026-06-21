const prisma = require('../config/database');

const createNotification = async (userId, title, message, type, actionUrl) => {
  await prisma.notification.create({
    data: { userId, title, message, type, actionUrl },
  });
};

const apply = async (req, res) => {
  try {
    const { internshipId, coverLetter, resumeUrl } = req.body;

    const student = await prisma.student.findUnique({ where: { userId: req.user.id } });
    if (!student) return res.status(404).json({ error: 'Student profile not found' });

    const internship = await prisma.internship.findUnique({
      where: { id: internshipId },
      include: { company: { include: { user: true } } },
    });

    if (!internship || internship.status !== 'OPEN') {
      return res.status(400).json({ error: 'Internship is not available for applications' });
    }

    const existing = await prisma.application.findUnique({
      where: { studentId_internshipId: { studentId: student.id, internshipId } },
    });

    if (existing) {
      return res.status(409).json({ error: 'You have already applied to this internship' });
    }

    const application = await prisma.application.create({
      data: {
        studentId: student.id,
        internshipId,
        coverLetter,
        resumeUrl,
      },
      include: {
        internship: {
          include: { company: { select: { name: true } } },
        },
      },
    });

    await createNotification(
      internship.company.userId,
      'New Application Received',
      `${student.firstName} ${student.lastName} applied for "${internship.title}"`,
      'APPLICATION_UPDATE',
      `/company/applications/${application.id}`
    );

    res.status(201).json(application);
  } catch (error) {
    console.error('Apply error:', error);
    res.status(500).json({ error: 'Failed to submit application' });
  }
};

const getStudentApplications = async (req, res) => {
  try {
    const student = await prisma.student.findUnique({ where: { userId: req.user.id } });
    if (!student) return res.status(404).json({ error: 'Student not found' });

    const { status } = req.query;
    const applications = await prisma.application.findMany({
      where: {
        studentId: student.id,
        ...(status && { status }),
      },
      include: {
        internship: {
          include: {
            company: { select: { name: true, logoUrl: true, location: true } },
            skills: { include: { skill: true } },
          },
        },
        interview: true,
      },
      orderBy: { appliedAt: 'desc' },
    });

    res.json(applications);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch applications' });
  }
};

const getCompanyApplications = async (req, res) => {
  try {
    const company = await prisma.company.findUnique({ where: { userId: req.user.id } });
    if (!company) return res.status(404).json({ error: 'Company not found' });

    const { internshipId, status, page = 1, limit = 20 } = req.query;
    const skip = (parseInt(page) - 1) * parseInt(limit);

    const where = {
      internship: { companyId: company.id },
      ...(internshipId && { internshipId }),
      ...(status && { status }),
    };

    const [applications, total] = await Promise.all([
      prisma.application.findMany({
        where,
        include: {
          student: {
            include: {
              user: { select: { email: true } },
              college: { select: { name: true } },
              program: { select: { name: true } },
              skills: { include: { skill: true } },
            },
          },
          internship: { select: { id: true, title: true } },
          interview: true,
        },
        orderBy: { appliedAt: 'desc' },
        skip,
        take: parseInt(limit),
      }),
      prisma.application.count({ where }),
    ]);

    res.json({
      applications,
      pagination: { total, page: parseInt(page), limit: parseInt(limit), pages: Math.ceil(total / parseInt(limit)) },
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch applications' });
  }
};

const updateStatus = async (req, res) => {
  try {
    const { id } = req.params;
    const { status, notes } = req.body;

    const company = await prisma.company.findUnique({ where: { userId: req.user.id } });

    const application = await prisma.application.findFirst({
      where: { id, internship: { companyId: company.id } },
      include: {
        student: { include: { user: true } },
        internship: true,
      },
    });

    if (!application) return res.status(404).json({ error: 'Application not found' });

    const updated = await prisma.application.update({
      where: { id },
      data: { status, notes },
    });

    const notifMessages = {
      SCREENING: 'Your application is being reviewed',
      SHORTLISTED: 'Congratulations! You have been shortlisted',
      INTERVIEW: 'You have been invited for an interview',
      SELECTED: 'Congratulations! You have been selected',
      REJECTED: 'Your application was not selected this time',
    };

    if (notifMessages[status]) {
      await createNotification(
        application.student.userId,
        `Application Update: ${application.internship.title}`,
        notifMessages[status],
        'APPLICATION_UPDATE',
        `/student/applications`
      );
    }

    // Auto-create enrollment if selected
    if (status === 'SELECTED') {
      await prisma.internshipEnrollment.upsert({
        where: {
          studentId_internshipId: {
            studentId: application.studentId,
            internshipId: application.internshipId,
          },
        },
        update: {},
        create: {
          studentId: application.studentId,
          internshipId: application.internshipId,
          startDate: application.internship.startDate || new Date(),
          endDate: application.internship.endDate,
        },
      });
    }

    res.json(updated);
  } catch (error) {
    console.error('Update status error:', error);
    res.status(500).json({ error: 'Failed to update application status' });
  }
};

const withdraw = async (req, res) => {
  try {
    const { id } = req.params;
    const student = await prisma.student.findUnique({ where: { userId: req.user.id } });

    const application = await prisma.application.findFirst({
      where: { id, studentId: student.id },
    });

    if (!application) return res.status(404).json({ error: 'Application not found' });

    if (['SELECTED', 'REJECTED'].includes(application.status)) {
      return res.status(400).json({ error: 'Cannot withdraw this application' });
    }

    const updated = await prisma.application.update({
      where: { id },
      data: { status: 'WITHDRAWN' },
    });

    res.json(updated);
  } catch (error) {
    res.status(500).json({ error: 'Failed to withdraw application' });
  }
};

const scheduleInterview = async (req, res) => {
  try {
    const { applicationId } = req.params;
    const { scheduledAt, mode, link, location, notes } = req.body;

    const company = await prisma.company.findUnique({ where: { userId: req.user.id } });

    const application = await prisma.application.findFirst({
      where: { id: applicationId, internship: { companyId: company.id } },
      include: { student: { include: { user: true } }, internship: true },
    });

    if (!application) return res.status(404).json({ error: 'Application not found' });

    const interview = await prisma.interview.upsert({
      where: { applicationId },
      update: { scheduledAt: new Date(scheduledAt), mode, link, location, notes },
      create: {
        applicationId,
        scheduledAt: new Date(scheduledAt),
        mode, link, location, notes,
      },
    });

    await prisma.application.update({
      where: { id: applicationId },
      data: { status: 'INTERVIEW' },
    });

    await createNotification(
      application.student.userId,
      'Interview Scheduled',
      `Interview for "${application.internship.title}" scheduled on ${new Date(scheduledAt).toLocaleDateString()}`,
      'INTERVIEW_SCHEDULED',
      '/student/applications'
    );

    res.json(interview);
  } catch (error) {
    res.status(500).json({ error: 'Failed to schedule interview' });
  }
};

module.exports = {
  apply, getStudentApplications, getCompanyApplications,
  updateStatus, withdraw, scheduleInterview,
};
