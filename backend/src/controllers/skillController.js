const prisma = require('../config/database');

const getAll = async (req, res) => {
  try {
    const { search, category } = req.query;
    const skills = await prisma.skill.findMany({
      where: {
        ...(search && { name: { contains: search, mode: 'insensitive' } }),
        ...(category && { category }),
      },
      orderBy: { name: 'asc' },
    });
    res.json(skills);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch skills' });
  }
};

const create = async (req, res) => {
  try {
    const { name, category } = req.body;
    const skill = await prisma.skill.create({ data: { name, category } });
    res.status(201).json(skill);
  } catch (error) {
    if (error.code === 'P2002') return res.status(409).json({ error: 'Skill already exists' });
    res.status(500).json({ error: 'Failed to create skill' });
  }
};

const update = async (req, res) => {
  try {
    const { id } = req.params;
    const { name, category } = req.body;
    const skill = await prisma.skill.update({ where: { id }, data: { name, category } });
    res.json(skill);
  } catch (error) {
    res.status(500).json({ error: 'Failed to update skill' });
  }
};

const remove = async (req, res) => {
  try {
    const { id } = req.params;
    await prisma.skill.delete({ where: { id } });
    res.json({ message: 'Skill deleted' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to delete skill' });
  }
};

module.exports = { getAll, create, update, remove };
