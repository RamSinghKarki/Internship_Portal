const prisma = require('../config/database');

const getProfile = async (req, res) => {
  try {
    const student = await prisma.student.findUnique({
      where: { userId: req.user.id },
      include: {
        user: { select: { email: true, createdAt: true } },
        college: { include: { university: true } },
        program: true,
        skills: { include: { skill: true } },
        documents: true,
      },
    });

    if (!student) return res.status(404).json({ error: 'Student not found' });
    res.json(student);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch profile' });
  }
};

const updateProfile = async (req, res) => {
  try {
    const {
      firstName, lastName, phone, registrationNumber, symbolNumber,
      semester, academicYear, collegeId, programId, location, bio, status, skills,
    } = req.body;

    const student = await prisma.student.findUnique({ where: { userId: req.user.id } });
    if (!student) return res.status(404).json({ error: 'Student not found' });

    const updatedStudent = await prisma.$transaction(async (tx) => {
      const updated = await tx.student.update({
        where: { userId: req.user.id },
        data: {
          firstName, lastName, phone, registrationNumber, symbolNumber,
          semester: semester ? parseInt(semester) : undefined,
          academicYear, collegeId, programId, location, bio, status,
        },
      });

      if (skills && Array.isArray(skills)) {
        await tx.studentSkill.deleteMany({ where: { studentId: student.id } });
        if (skills.length > 0) {
          await tx.studentSkill.createMany({
            data: skills.map((s) => ({
              studentId: student.id,
              skillId: s.skillId || s,
              proficiency: s.proficiency,
            })),
          });
        }
      }

      return updated;
    });

    const fullStudent = await prisma.student.findUnique({
      where: { id: student.id },
      include: {
        college: { include: { university: true } },
        program: true,
        skills: { include: { skill: true } },
      },
    });

    res.json(fullStudent);
  } catch (error) {
    console.error('Update profile error:', error);
    res.status(500).json({ error: 'Failed to update profile' });
  }
};

const uploadAvatar = async (req, res) => {
  try {
    if (!req.file) return res.status(400).json({ error: 'No file uploaded' });

    const avatarUrl = `/uploads/avatars/${req.file.filename}`;
    await prisma.student.update({
      where: { userId: req.user.id },
      data: { avatarUrl },
    });

    res.json({ avatarUrl, message: 'Avatar updated successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to upload avatar' });
  }
};

const getDocuments = async (req, res) => {
  try {
    const student = await prisma.student.findUnique({ where: { userId: req.user.id } });
    if (!student) return res.status(404).json({ error: 'Student not found' });

    const documents = await prisma.document.findMany({
      where: { studentId: student.id },
      orderBy: { uploadedAt: 'desc' },
    });

    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch documents' });
  }
};

const uploadDocument = async (req, res) => {
  try {
    if (!req.file) return res.status(400).json({ error: 'No file uploaded' });

    const student = await prisma.student.findUnique({ where: { userId: req.user.id } });
    if (!student) return res.status(404).json({ error: 'Student not found' });

    const { type, name } = req.body;
    const document = await prisma.document.create({
      data: {
        studentId: student.id,
        type: type || 'OTHER',
        name: name || req.file.originalname,
        filename: req.file.filename,
        path: `/uploads/documents/${req.file.filename}`,
        mimeType: req.file.mimetype,
        size: req.file.size,
      },
    });

    res.status(201).json(document);
  } catch (error) {
    res.status(500).json({ error: 'Failed to upload document' });
  }
};

const deleteDocument = async (req, res) => {
  try {
    const { documentId } = req.params;
    const student = await prisma.student.findUnique({ where: { userId: req.user.id } });

    const document = await prisma.document.findFirst({
      where: { id: documentId, studentId: student.id },
    });

    if (!document) return res.status(404).json({ error: 'Document not found' });

    await prisma.document.delete({ where: { id: documentId } });
    res.json({ message: 'Document deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to delete document' });
  }
};

const getEnrollments = async (req, res) => {
  try {
    const student = await prisma.student.findUnique({ where: { userId: req.user.id } });
    if (!student) return res.status(404).json({ error: 'Student not found' });

    const enrollments = await prisma.internshipEnrollment.findMany({
      where: { studentId: student.id },
      include: {
        internship: { include: { company: { select: { name: true, logoUrl: true } } } },
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

const getDashboardStats = async (req, res) => {
  try {
    const student = await prisma.student.findUnique({ where: { userId: req.user.id } });
    if (!student) return res.status(404).json({ error: 'Student not found' });

    const [applications, enrollments, progressLogs] = await Promise.all([
      prisma.application.count({ where: { studentId: student.id } }),
      prisma.internshipEnrollment.count({ where: { studentId: student.id } }),
      prisma.progressLog.count({
        where: { enrollment: { studentId: student.id } },
      }),
    ]);

    const recentApplications = await prisma.application.findMany({
      where: { studentId: student.id },
      include: {
        internship: {
          include: { company: { select: { name: true, logoUrl: true } } },
        },
      },
      orderBy: { appliedAt: 'desc' },
      take: 5,
    });

    const activeEnrollment = await prisma.internshipEnrollment.findFirst({
      where: { studentId: student.id, status: 'ACTIVE' },
      include: {
        internship: { include: { company: { select: { name: true } } } },
        _count: { select: { progressLogs: true } },
      },
    });

    res.json({
      stats: { applications, enrollments, progressLogs },
      recentApplications,
      activeEnrollment,
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch dashboard stats' });
  }
};

module.exports = {
  getProfile, updateProfile, uploadAvatar,
  getDocuments, uploadDocument, deleteDocument,
  getEnrollments, getDashboardStats,
};
