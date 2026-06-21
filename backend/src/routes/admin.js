const express = require('express');
const router = express.Router();
const { authenticate } = require('../middleware/auth');
const { roleCheck } = require('../middleware/roleCheck');
const {
  getStats, getUsers, updateUser, verifyCompany,
  getUniversities, createUniversity, getColleges, createCollege,
  getEnrollments, assignInternalSupervisor, getInternalSupervisors, getCompanies,
} = require('../controllers/adminController');

router.use(authenticate, roleCheck('ADMIN'));

router.get('/stats', getStats);
router.get('/users', getUsers);
router.put('/users/:id', updateUser);
router.get('/companies', getCompanies);
router.put('/companies/:id/verify', verifyCompany);
router.get('/universities', getUniversities);
router.post('/universities', createUniversity);
router.get('/colleges', getColleges);
router.post('/colleges', createCollege);
router.get('/enrollments', getEnrollments);
router.put('/enrollments/:enrollmentId/supervisor', assignInternalSupervisor);
router.get('/supervisors/internal', getInternalSupervisors);

module.exports = router;
