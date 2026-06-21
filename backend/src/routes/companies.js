const express = require('express');
const router = express.Router();
const { authenticate } = require('../middleware/auth');
const { roleCheck } = require('../middleware/roleCheck');
const { upload } = require('../middleware/upload');
const {
  getProfile, updateProfile, uploadLogo,
  getDashboardStats, getEnrollments, assignSupervisor,
} = require('../controllers/companyController');

router.use(authenticate, roleCheck('COMPANY'));

router.get('/profile', getProfile);
router.put('/profile', updateProfile);
router.post('/logo', (req, res, next) => { req.uploadSubDir = 'logos'; next(); }, upload.single('logo'), uploadLogo);
router.get('/dashboard', getDashboardStats);
router.get('/enrollments', getEnrollments);
router.put('/enrollments/:enrollmentId/supervisor', assignSupervisor);

module.exports = router;
