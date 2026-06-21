const prisma = require('../config/database');

const getStats = async (req, res) => {
  try {
    const [students, companies, internships, applications, enrollments, verifiedCompanies, openInternships, activeEnrollments] = await Promise.all([
      prisma.student.count(),
      prisma.company.count(),
      prisma.internship.count(),
      prisma.application.count(),
      prisma.internshipEnrollment.count(),
      prisma.company.count({ where: { isVerified: true } }),
      prisma.internship.count({ where: { status: 'OPEN' } }),
      prisma.internshipEnrollment.count({ where: { status: 'ACTIVE' } }),
    ]);

    const recentUsers = await prisma.user.findMany({
      orderBy: { createdAt: 'desc' },
      take: 10,
      select: {
        id: true, email: true, role: true, isActive: true, createdAt: true,
        student: { select: { firstName: true, lastName: true } },
        company: { select: { name: true } },
        supervisor: { select: { firstName: true, lastName: true } },
        admin: { select: { firstName: true, lastName: true } },
      },
    });

    res.json({
      stats: { students, companies, verifiedCompanies, internships, openInternships, applications, enrollments, activeEnrollments },
      recentUsers,
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch stats' });
  }
};

const getUsers = async (req, res) => {
  try {
    const { role, search, isActive, page = 1, limit = 20 } = req.query;
    const skip = (parseInt(page) - 1) * parseInt(limit);

    const where = {
      ...(role && { role }),
      ...(isActive !== undefined && { isActive: isActive === 'true' }),
      ...(search && { email: { contains: search, mode: 'insensitive' } }),
    };

    const [users, total] = await Promise.all([
      prisma.user.findMany({
        where,
        select: {
          id: true, email: true, role: true, isActive: true, createdAt: true,
          student: { select: { firstName: true, lastName: true, registrationNumber: true } },
          company: { select: { name: true, isVerified: true, industry: true } },
          supervisor: { select: { firstName: true, lastName: true, type: true } },
          admin: { select: { firstName: true, lastName: true } },
        },
        orderBy: { createdAt: 'desc' },
        skip,
        take: parseInt(limit),
      }),
      prisma.user.count({ where }),
    ]);

    res.json({
      users,
      pagination: { total, page: parseInt(page), limit: parseInt(limit), pages: Math.ceil(total / parseInt(limit)) },
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch users' });
  }
};

const updateUser = async (req, res) => {
  try {
    const { id } = req.params;
    const { isActive } = req.body;

    const user = await prisma.user.update({
      where: { id },
      data: { isActive },
      select: { id: true, email: true, role: true, isActive: true },
    });

    res.json(user);
  } catch (error) {
    res.status(500).json({ error: 'Failed to update user' });
  }
};

const verifyCompany = async (req, res) => {
  try {
    const { id } = req.params;
    const { isVerified } = req.body;

    const company = await prisma.company.update({
      where: { id },
      data: { isVerified },
    });

    res.json(company);
  } catch (error) {
    res.status(500).json({ error: 'Failed to update company' });
  }
};

const getUniversities = async (req, res) => {
  try {
    const universities = await prisma.university.findMany({
      include: { _count: { select: { colleges: true } } },
      orderBy: { name: 'asc' },
    });
    res.json(universities);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch universities' });
  }
};

const createUniversity = async (req, res) => {
  try {
    const { name, location, website } = req.body;
    const university = await prisma.university.create({ data: { name, location, website } });
    res.status(201).json(university);
  } catch (error) {
    if (error.code === 'P2002') return res.status(409).json({ error: 'University already exists' });
    res.status(500).json({ error: 'Failed to create university' });
  }
};

const getColleges = async (req, res) => {
  try {
    const colleges = await prisma.college.findMany({
      include: {
        university: { select: { name: true } },
        _count: { select: { students: true, programs: true } },
      },
      orderBy: { name: 'asc' },
    });
    res.json(colleges);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch colleges' });
  }
};

const createCollege = async (req, res) => {
  try {
    const { name, universityId, location } = req.body;
    const college = await prisma.college.create({ data: { name, universityId, location } });
    res.status(201).json(college);
  } catch (error) {
    res.status(500).json({ error: 'Failed to create college' });
  }
};

const getEnrollments = async (req, res) => {
  try {
    const { status, page = 1, limit = 20 } = req.query;
    const skip = (parseInt(page) - 1) * parseInt(limit);
    const where = { ...(status && { status }) };

    const [enrollments, total] = await Promise.all([
      prisma.internshipEnrollment.findMany({
        where,
        include: {
          student: { select: { firstName: true, lastName: true } },
          internship: { include: { company: { select: { name: true } } } },
          internalSupervisor: { select: { firstName: true, lastName: true } },
          externalSupervisor: { select: { firstName: true, lastName: true } },
        },
        orderBy: { createdAt: 'desc' },
        skip,
        take: parseInt(limit),
      }),
      prisma.internshipEnrollment.count({ where }),
    ]);

    res.json({
      enrollments,
      pagination: { total, page: parseInt(page), limit: parseInt(limit), pages: Math.ceil(total / parseInt(limit)) },
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch enrollments' });
  }
};

const assignInternalSupervisor = async (req, res) => {
  try {
    const { enrollmentId } = req.params;
    const { supervisorId } = req.body;

    const enrollment = await prisma.internshipEnrollment.update({
      where: { id: enrollmentId },
      data: { internalSupervisorId: supervisorId },
    });

    res.json(enrollment);
  } catch (error) {
    res.status(500).json({ error: 'Failed to assign supervisor' });
  }
};

const getInternalSupervisors = async (req, res) => {
  try {
    const supervisors = await prisma.supervisor.findMany({
      where: { type: 'INTERNAL' },
      include: {
        user: { select: { email: true } },
        college: { select: { name: true } },
        _count: { select: { internalEnrollments: true } },
      },
    });
    res.json(supervisors);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch supervisors' });
  }
};

const getCompanies = async (req, res) => {
  try {
    const { isVerified, search, page = 1, limit = 20 } = req.query;
    const skip = (parseInt(page) - 1) * parseInt(limit);

    const where = {
      ...(isVerified !== undefined && { isVerified: isVerified === 'true' }),
      ...(search && { name: { contains: search, mode: 'insensitive' } }),
    };

    const [companies, total] = await Promise.all([
      prisma.company.findMany({
        where,
        include: {
          user: { select: { email: true, isActive: true } },
          _count: { select: { internships: true } },
        },
        orderBy: { createdAt: 'desc' },
        skip,
        take: parseInt(limit),
      }),
      prisma.company.count({ where }),
    ]);

    res.json({
      companies,
      pagination: { total, page: parseInt(page), limit: parseInt(limit), pages: Math.ceil(total / parseInt(limit)) },
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch companies' });
  }
};

module.exports = {
  getStats, getUsers, updateUser, verifyCompany,
  getUniversities, createUniversity, getColleges, createCollege,
  getEnrollments, assignInternalSupervisor, getInternalSupervisors, getCompanies,
};
