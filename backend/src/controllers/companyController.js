const prisma = require('../config/database');

const getProfile = async (req, res) => {
  try {
    const company = await prisma.company.findUnique({
      where: { userId: req.user.id },
      include: {
        user: { select: { email: true, createdAt: true } },
        _count: { select: { internships: true } },
      },
    });
    if (!company) return res.status(404).json({ error: 'Company not found' });
    res.json(company);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch profile' });
  }
};

const updateProfile = async (req, res) => {
  try {
    const { name, description, industry, website, location, size } = req.body;

    const company = await prisma.company.update({
      where: { userId: req.user.id },
      data: { name, description, industry, website, location, size },
    });

    res.json(company);
  } catch (error) {
    res.status(500).json({ error: 'Failed to update profile' });
  }
};

const uploadLogo = async (req, res) => {
  try {
    if (!req.file) return res.status(400).json({ error: 'No file uploaded' });

    const logoUrl = `/uploads/logos/${req.file.filename}`;
    const company = await prisma.company.update({
      where: { userId: req.user.id },
      data: { logoUrl },
    });

    res.json({ logoUrl, message: 'Logo updated successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to upload logo' });
  }
};

const getDashboardStats = async (req, res) => {
  try {
    const company = await prisma.company.findUnique({ where: { userId: req.user.id } });
    if (!company) return res.status(404).json({ error: 'Company not found' });

    const [totalInternships, openInternships, totalApplications, activeEnrollments] = await Promise.all([
      prisma.internship.count({ where: { companyId: company.id } }),
      prisma.internship.count({ where: { companyId: company.id, status: 'OPEN' } }),
      prisma.application.count({ where: { internship: { companyId: company.id } } }),
      prisma.internshipEnrollment.count({
        where: { internship: { companyId: company.id }, status: 'ACTIVE' },
      }),
    ]);

    const applicationsByStatus = await prisma.application.groupBy({
      by: ['status'],
      where: { internship: { companyId: company.id } },
      _count: true,
    });

    const recentApplications = await prisma.application.findMany({
      where: { internship: { companyId: company.id } },
      include: {
        student: { select: { firstName: true, lastName: true, avatarUrl: true } },
        internship: { select: { title: true } },
      },
      orderBy: { appliedAt: 'desc' },
      take: 5,
    });

    res.json({
      stats: { totalInternships, openInternships, totalApplications, activeEnrollments },
      applicationsByStatus,
      recentApplications,
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch dashboard stats' });
  }
};

const getEnrollments = async (req, res) => {
  try {
    const company = await prisma.company.findUnique({ where: { userId: req.user.id } });
    if (!company) return res.status(404).json({ error: 'Company not found' });

    const { status, internshipId } = req.query;
    const where = {
      internship: { companyId: company.id },
      ...(status && { status }),
      ...(internshipId && { internshipId }),
    };

    const enrollments = await prisma.internshipEnrollment.findMany({
      where,
      include: {
        student: {
          include: {
            user: { select: { email: true } },
            college: { select: { name: true } },
          },
        },
        internship: { select: { title: true } },
        internalSupervisor: { select: { firstName: true, lastName: true } },
        externalSupervisor: { select: { firstName: true, lastName: true } },
        evaluation: true,
        _count: { select: { progressLogs: true } },
      },
      orderBy: { createdAt: 'desc' },
    });

    res.json(enrollments);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch enrollments' });
  }
};

const assignSupervisor = async (req, res) => {
  try {
    const { enrollmentId } = req.params;
    const { supervisorId, type } = req.body;

    const company = await prisma.company.findUnique({ where: { userId: req.user.id } });

    const enrollment = await prisma.internshipEnrollment.findFirst({
      where: { id: enrollmentId, internship: { companyId: company.id } },
    });

    if (!enrollment) return res.status(404).json({ error: 'Enrollment not found' });

    const updateData = type === 'INTERNAL'
      ? { internalSupervisorId: supervisorId }
      : { externalSupervisorId: supervisorId };

    const updated = await prisma.internshipEnrollment.update({
      where: { id: enrollmentId },
      data: updateData,
    });

    res.json(updated);
  } catch (error) {
    res.status(500).json({ error: 'Failed to assign supervisor' });
  }
};

module.exports = {
  getProfile, updateProfile, uploadLogo,
  getDashboardStats, getEnrollments, assignSupervisor,
};
