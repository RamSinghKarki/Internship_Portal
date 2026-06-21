const { PrismaClient } = require('@prisma/client');
const bcrypt = require('bcryptjs');

const prisma = new PrismaClient();

async function main() {
  console.log('Seeding database...');

  // Create Universities
  const university = await prisma.university.upsert({
    where: { name: 'Tribhuvan University' },
    update: {},
    create: {
      name: 'Tribhuvan University',
      location: 'Kathmandu, Nepal',
      website: 'https://tu.edu.np',
    },
  });

  const university2 = await prisma.university.upsert({
    where: { name: 'Pokhara University' },
    update: {},
    create: {
      name: 'Pokhara University',
      location: 'Pokhara, Nepal',
    },
  });

  // Create Colleges
  const college = await prisma.college.create({
    data: {
      name: 'Kathmandu College of Management',
      universityId: university.id,
      location: 'Kathmandu, Nepal',
      isVerified: true,
    },
  });

  const college2 = await prisma.college.create({
    data: {
      name: 'Kantipur Engineering College',
      universityId: university.id,
      location: 'Dhapakhel, Lalitpur',
      isVerified: true,
    },
  });

  // Create Programs
  const program1 = await prisma.program.create({
    data: {
      name: 'Bachelor of Business Administration (BBA)',
      collegeId: college.id,
      duration: 8,
    },
  });

  const program2 = await prisma.program.create({
    data: {
      name: 'Bachelor of Computer Engineering',
      collegeId: college2.id,
      duration: 8,
    },
  });

  // Create Skills
  const skillNames = [
    { name: 'JavaScript', category: 'Programming' },
    { name: 'React.js', category: 'Frontend' },
    { name: 'Node.js', category: 'Backend' },
    { name: 'Python', category: 'Programming' },
    { name: 'Django', category: 'Backend' },
    { name: 'SQL', category: 'Database' },
    { name: 'PostgreSQL', category: 'Database' },
    { name: 'MongoDB', category: 'Database' },
    { name: 'Java', category: 'Programming' },
    { name: 'Spring Boot', category: 'Backend' },
    { name: 'HTML/CSS', category: 'Frontend' },
    { name: 'UI/UX Design', category: 'Design' },
    { name: 'Digital Marketing', category: 'Marketing' },
    { name: 'Data Analysis', category: 'Analytics' },
    { name: 'Machine Learning', category: 'AI/ML' },
    { name: 'Communication', category: 'Soft Skills' },
    { name: 'Leadership', category: 'Soft Skills' },
    { name: 'Project Management', category: 'Management' },
    { name: 'Financial Analysis', category: 'Finance' },
    { name: 'Accounting', category: 'Finance' },
  ];

  const skills = {};
  for (const s of skillNames) {
    const skill = await prisma.skill.upsert({
      where: { name: s.name },
      update: {},
      create: s,
    });
    skills[s.name] = skill;
  }

  // Create Admin
  const adminPassword = await bcrypt.hash('Admin@123', 12);
  const adminUser = await prisma.user.upsert({
    where: { email: 'admin@internportal.com' },
    update: {},
    create: {
      email: 'admin@internportal.com',
      password: adminPassword,
      role: 'ADMIN',
      admin: {
        create: {
          firstName: 'System',
          lastName: 'Admin',
        },
      },
    },
  });

  // Create Company
  const companyPassword = await bcrypt.hash('Company@123', 12);
  const companyUser = await prisma.user.upsert({
    where: { email: 'hr@techcorp.com' },
    update: {},
    create: {
      email: 'hr@techcorp.com',
      password: companyPassword,
      role: 'COMPANY',
      company: {
        create: {
          name: 'TechCorp Solutions',
          description: 'Leading software development company specializing in enterprise solutions.',
          industry: 'Information Technology',
          website: 'https://techcorp.com',
          location: 'Kathmandu, Nepal',
          size: '50-200',
          isVerified: true,
        },
      },
    },
  });

  const company2Password = await bcrypt.hash('Company@123', 12);
  const companyUser2 = await prisma.user.upsert({
    where: { email: 'hr@digitalnepal.com' },
    update: {},
    create: {
      email: 'hr@digitalnepal.com',
      password: company2Password,
      role: 'COMPANY',
      company: {
        create: {
          name: 'Digital Nepal Pvt. Ltd.',
          description: 'Digital transformation and IT consulting firm.',
          industry: 'Consulting',
          website: 'https://digitalnepal.com',
          location: 'Lalitpur, Nepal',
          size: '10-50',
          isVerified: true,
        },
      },
    },
  });

  // Get company data
  const company = await prisma.company.findUnique({ where: { userId: companyUser.id } });
  const company2 = await prisma.company.findUnique({ where: { userId: companyUser2.id } });

  // Create Internships
  await prisma.internship.create({
    data: {
      companyId: company.id,
      title: 'Full Stack Web Developer Intern',
      description: 'Join our dynamic team and work on real-world web applications. You will be involved in building scalable web applications using modern technologies.',
      requirements: 'Basic knowledge of HTML, CSS, JavaScript. Familiarity with React or Vue.js is a plus.',
      responsibilities: 'Develop and maintain web applications, collaborate with senior developers, participate in code reviews.',
      stipend: 15000,
      isPaid: true,
      duration: 12,
      vacancies: 3,
      location: 'Kathmandu, Nepal',
      mode: 'ONSITE',
      status: 'OPEN',
      deadline: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
      skills: {
        create: [
          { skillId: skills['JavaScript'].id },
          { skillId: skills['React.js'].id },
          { skillId: skills['Node.js'].id },
          { skillId: skills['HTML/CSS'].id },
        ],
      },
    },
  });

  await prisma.internship.create({
    data: {
      companyId: company.id,
      title: 'Python Backend Developer Intern',
      description: 'Work on backend systems and APIs using Python and Django framework.',
      requirements: 'Knowledge of Python, basic understanding of REST APIs and databases.',
      stipend: 12000,
      isPaid: true,
      duration: 8,
      vacancies: 2,
      location: 'Kathmandu, Nepal',
      mode: 'HYBRID',
      status: 'OPEN',
      deadline: new Date(Date.now() + 45 * 24 * 60 * 60 * 1000),
      skills: {
        create: [
          { skillId: skills['Python'].id },
          { skillId: skills['Django'].id },
          { skillId: skills['PostgreSQL'].id },
        ],
      },
    },
  });

  await prisma.internship.create({
    data: {
      companyId: company2.id,
      title: 'Digital Marketing Intern',
      description: 'Learn and contribute to digital marketing campaigns, SEO, and social media management.',
      requirements: 'Interest in digital marketing, good communication skills, basic knowledge of social media platforms.',
      stipend: 8000,
      isPaid: true,
      duration: 6,
      vacancies: 2,
      location: 'Lalitpur, Nepal',
      mode: 'ONSITE',
      status: 'OPEN',
      deadline: new Date(Date.now() + 20 * 24 * 60 * 60 * 1000),
      skills: {
        create: [
          { skillId: skills['Digital Marketing'].id },
          { skillId: skills['Communication'].id },
        ],
      },
    },
  });

  await prisma.internship.create({
    data: {
      companyId: company2.id,
      title: 'Data Analysis Intern',
      description: 'Help analyze business data, create reports, and derive insights to support decision-making.',
      requirements: 'Knowledge of Excel, basic SQL, interest in data and analytics.',
      stipend: 10000,
      isPaid: true,
      duration: 10,
      vacancies: 1,
      location: 'Remote',
      mode: 'REMOTE',
      status: 'OPEN',
      deadline: new Date(Date.now() + 15 * 24 * 60 * 60 * 1000),
      skills: {
        create: [
          { skillId: skills['Data Analysis'].id },
          { skillId: skills['SQL'].id },
          { skillId: skills['Python'].id },
        ],
      },
    },
  });

  // Create Internal Supervisor
  const supervisorPassword = await bcrypt.hash('Supervisor@123', 12);
  await prisma.user.upsert({
    where: { email: 'supervisor@kcm.edu.np' },
    update: {},
    create: {
      email: 'supervisor@kcm.edu.np',
      password: supervisorPassword,
      role: 'INTERNAL_SUPERVISOR',
      supervisor: {
        create: {
          firstName: 'Ram',
          lastName: 'Sharma',
          type: 'INTERNAL',
          expertise: 'Software Engineering',
          collegeId: college.id,
          phone: '9841000001',
        },
      },
    },
  });

  // Create Student
  const studentPassword = await bcrypt.hash('Student@123', 12);
  const studentUser = await prisma.user.upsert({
    where: { email: 'student@example.com' },
    update: {},
    create: {
      email: 'student@example.com',
      password: studentPassword,
      role: 'STUDENT',
      student: {
        create: {
          firstName: 'Sita',
          lastName: 'Thapa',
          phone: '9841000002',
          registrationNumber: '075-BCT-101',
          symbolNumber: '12345',
          semester: 7,
          collegeId: college2.id,
          programId: program2.id,
          location: 'Kathmandu, Nepal',
          bio: 'Computer Engineering student with passion for web development.',
          status: 'CURRENT',
        },
      },
    },
  });

  console.log('✅ Seed completed successfully!');
  console.log('\n📝 Test Credentials:');
  console.log('Admin:    admin@internportal.com / Admin@123');
  console.log('Company:  hr@techcorp.com / Company@123');
  console.log('Company:  hr@digitalnepal.com / Company@123');
  console.log('Supervisor: supervisor@kcm.edu.np / Supervisor@123');
  console.log('Student:  student@example.com / Student@123');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
