const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { validationResult } = require('express-validator');
const prisma = require('../config/database');

const generateToken = (userId) =>
  jwt.sign({ userId }, process.env.JWT_SECRET, {
    expiresIn: process.env.JWT_EXPIRES_IN || '7d',
  });

const register = async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { email, password, role, firstName, lastName, companyName, industry, location, phone } = req.body;

    const existingUser = await prisma.user.findUnique({ where: { email } });
    if (existingUser) {
      return res.status(409).json({ error: 'Email already registered' });
    }

    const hashedPassword = await bcrypt.hash(password, 12);

    const user = await prisma.$transaction(async (tx) => {
      const newUser = await tx.user.create({
        data: { email, password: hashedPassword, role },
      });

      if (role === 'STUDENT') {
        await tx.student.create({
          data: { userId: newUser.id, firstName, lastName, phone },
        });
      } else if (role === 'COMPANY') {
        await tx.company.create({
          data: { userId: newUser.id, name: companyName || firstName, industry, location },
        });
      } else if (role === 'INTERNAL_SUPERVISOR') {
        await tx.supervisor.create({
          data: { userId: newUser.id, firstName, lastName, type: 'INTERNAL', phone },
        });
      } else if (role === 'EXTERNAL_SUPERVISOR') {
        await tx.supervisor.create({
          data: { userId: newUser.id, firstName, lastName, type: 'EXTERNAL', phone },
        });
      } else if (role === 'ADMIN') {
        await tx.admin.create({
          data: { userId: newUser.id, firstName: firstName || 'Admin', lastName: lastName || 'User' },
        });
      }

      return newUser;
    });

    const token = generateToken(user.id);
    res.status(201).json({
      message: 'Registration successful',
      token,
      user: { id: user.id, email: user.email, role: user.role },
    });
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ error: 'Registration failed' });
  }
};

const login = async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { email, password } = req.body;

    const user = await prisma.user.findUnique({
      where: { email },
      include: {
        student: { select: { id: true, firstName: true, lastName: true, avatarUrl: true } },
        company: { select: { id: true, name: true, logoUrl: true, isVerified: true } },
        supervisor: { select: { id: true, firstName: true, lastName: true, type: true } },
        admin: { select: { id: true, firstName: true, lastName: true } },
      },
    });

    if (!user || !user.isActive) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const isPasswordValid = await bcrypt.compare(password, user.password);
    if (!isPasswordValid) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const token = generateToken(user.id);

    let profile = null;
    if (user.role === 'STUDENT') profile = user.student;
    else if (user.role === 'COMPANY') profile = user.company;
    else if (user.role === 'INTERNAL_SUPERVISOR' || user.role === 'EXTERNAL_SUPERVISOR') profile = user.supervisor;
    else if (user.role === 'ADMIN') profile = user.admin;

    res.json({
      message: 'Login successful',
      token,
      user: { id: user.id, email: user.email, role: user.role, profile },
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Login failed' });
  }
};

const getMe = async (req, res) => {
  try {
    const user = await prisma.user.findUnique({
      where: { id: req.user.id },
      include: {
        student: {
          include: {
            college: { include: { university: true } },
            program: true,
            skills: { include: { skill: true } },
          },
        },
        company: true,
        supervisor: { include: { college: true, company: true } },
        admin: true,
      },
    });

    const { password, ...userWithoutPassword } = user;
    res.json(userWithoutPassword);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch profile' });
  }
};

const changePassword = async (req, res) => {
  try {
    const { currentPassword, newPassword } = req.body;

    const user = await prisma.user.findUnique({ where: { id: req.user.id } });
    const isValid = await bcrypt.compare(currentPassword, user.password);
    if (!isValid) {
      return res.status(400).json({ error: 'Current password is incorrect' });
    }

    const hashedPassword = await bcrypt.hash(newPassword, 12);
    await prisma.user.update({
      where: { id: req.user.id },
      data: { password: hashedPassword },
    });

    res.json({ message: 'Password changed successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to change password' });
  }
};

module.exports = { register, login, getMe, changePassword };
