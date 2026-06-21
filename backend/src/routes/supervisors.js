const express = require('express');
const router = express.Router();
const { authenticate } = require('../middleware/auth');
const { roleCheck } = require('../middleware/roleCheck');
const { getProfile, updateProfile, getAssignedEnrollments, getDashboardStats } = require('../controllers/supervisorController');

router.use(authenticate, roleCheck('INTERNAL_SUPERVISOR', 'EXTERNAL_SUPERVISOR'));

router.get('/profile', getProfile);
router.put('/profile', updateProfile);
router.get('/enrollments', getAssignedEnrollments);
router.get('/dashboard', getDashboardStats);

module.exports = router;
