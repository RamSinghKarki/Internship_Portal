const prisma = require('../config/database');

const getAll = async (req, res) => {
  try {
    const {
      search, status = 'OPEN', mode, location, skills,
      minStipend, isPaid, page = 1, limit = 12,
    } = req.query;

    const skip = (parseInt(page) - 1) * parseInt(limit);

    const where = {
      ...(status && { status }),
      ...(mode && { mode }),
      ...(location && { location: { contains: location, mode: 'insensitive' } }),
      ...(isPaid !== undefined && { isPaid: isPaid === 'true' }),
      ...(minStipend && { stipend: { gte: parseFloat(minStipend) } }),
      ...(search && {
        OR: [
          { title: { contains: search, mode: 'insensitive' } },
          { description: { contains: search, mode: 'insensitive' } },
          { company: { name: { contains: search, mode: 'insensitive' } } },
        ],
      }),
      ...(skills && {
        skills: {
          some: {
            skill: { name: { in: skills.split(',') } },
          },
        },
      }),
    };

    const [internships, total] = await Promise.all([
      prisma.internship.findMany({
        where,
        include: {
          company: { select: { id: true, name: true, logoUrl: true, location: true, isVerified: true } },
          skills: { include: { skill: true } },
          _count: { select: { applications: true } },
        },
        orderBy: { createdAt: 'desc' },
        skip,
        take: parseInt(limit),
      }),
      prisma.internship.count({ where }),
    ]);

    res.json({
      internships,
      pagination: {
        total,
        page: parseInt(page),
        limit: parseInt(limit),
        pages: Math.ceil(total / parseInt(limit)),
      },
    });
  } catch (error) {
    console.error('Get internships error:', error);
    res.status(500).json({ error: 'Failed to fetch internships' });
  }
};

const getById = async (req, res) => {
  try {
    const { id } = req.params;

    const internship = await prisma.internship.findUnique({
      where: { id },
      include: {
        company: {
          select: { id: true, name: true, logoUrl: true, location: true, isVerified: true, description: true, website: true, industry: true, size: true },
        },
        skills: { include: { skill: true } },
        _count: { select: { applications: true, enrollments: true } },
      },
    });

    if (!internship) return res.status(404).json({ error: 'Internship not found' });
    res.json(internship);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch internship' });
  }
};

const create = async (req, res) => {
  try {
    const company = await prisma.company.findUnique({ where: { userId: req.user.id } });
    if (!company) return res.status(404).json({ error: 'Company not found' });

    const {
      title, description, requirements, responsibilities,
      stipend, isPaid, duration, vacancies, location, mode,
      startDate, endDate, deadline, skills,
    } = req.body;

    const internship = await prisma.internship.create({
      data: {
        companyId: company.id,
        title,
        description,
        requirements,
        responsibilities,
        stipend: stipend ? parseFloat(stipend) : null,
        isPaid: isPaid || false,
        duration: parseInt(duration),
        vacancies: parseInt(vacancies) || 1,
        location,
        mode: mode || 'ONSITE',
        startDate: startDate ? new Date(startDate) : null,
        endDate: endDate ? new Date(endDate) : null,
        deadline: deadline ? new Date(deadline) : null,
        skills: skills && skills.length > 0 ? {
          create: skills.map((skillId) => ({ skillId })),
        } : undefined,
      },
      include: {
        company: { select: { name: true, logoUrl: true } },
        skills: { include: { skill: true } },
      },
    });

    res.status(201).json(internship);
  } catch (error) {
    console.error('Create internship error:', error);
    res.status(500).json({ error: 'Failed to create internship' });
  }
};

const update = async (req, res) => {
  try {
    const { id } = req.params;
    const company = await prisma.company.findUnique({ where: { userId: req.user.id } });

    const internship = await prisma.internship.findFirst({
      where: { id, companyId: company.id },
    });

    if (!internship) return res.status(404).json({ error: 'Internship not found' });

    const {
      title, description, requirements, responsibilities,
      stipend, isPaid, duration, vacancies, location, mode, status,
      startDate, endDate, deadline, skills,
    } = req.body;

    const updated = await prisma.$transaction(async (tx) => {
      if (skills !== undefined) {
        await tx.internshipSkill.deleteMany({ where: { internshipId: id } });
        if (skills.length > 0) {
          await tx.internshipSkill.createMany({
            data: skills.map((skillId) => ({ internshipId: id, skillId })),
          });
        }
      }

      return tx.internship.update({
        where: { id },
        data: {
          title, description, requirements, responsibilities,
          stipend: stipend ? parseFloat(stipend) : undefined,
          isPaid, duration: duration ? parseInt(duration) : undefined,
          vacancies: vacancies ? parseInt(vacancies) : undefined,
          location, mode, status,
          startDate: startDate ? new Date(startDate) : undefined,
          endDate: endDate ? new Date(endDate) : undefined,
          deadline: deadline ? new Date(deadline) : undefined,
        },
        include: {
          skills: { include: { skill: true } },
          _count: { select: { applications: true } },
        },
      });
    });

    res.json(updated);
  } catch (error) {
    res.status(500).json({ error: 'Failed to update internship' });
  }
};

const remove = async (req, res) => {
  try {
    const { id } = req.params;
    const company = await prisma.company.findUnique({ where: { userId: req.user.id } });

    const internship = await prisma.internship.findFirst({
      where: { id, companyId: company.id },
    });

    if (!internship) return res.status(404).json({ error: 'Internship not found' });

    await prisma.internship.delete({ where: { id } });
    res.json({ message: 'Internship deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to delete internship' });
  }
};

const getCompanyInternships = async (req, res) => {
  try {
    const company = await prisma.company.findUnique({ where: { userId: req.user.id } });
    if (!company) return res.status(404).json({ error: 'Company not found' });

    const { status } = req.query;
    const internships = await prisma.internship.findMany({
      where: {
        companyId: company.id,
        ...(status && { status }),
      },
      include: {
        skills: { include: { skill: true } },
        _count: { select: { applications: true, enrollments: true } },
      },
      orderBy: { createdAt: 'desc' },
    });

    res.json(internships);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch internships' });
  }
};

module.exports = { getAll, getById, create, update, remove, getCompanyInternships };
