const express = require('express');
const router = express.Router();
const { authenticate } = require('../middleware/auth');
const { roleCheck } = require('../middleware/roleCheck');
const {
  apply, getStudentApplications, getCompanyApplications,
  updateStatus, withdraw, scheduleInterview,
} = require('../controllers/applicationController');

router.use(authenticate);

router.post('/', roleCheck('STUDENT'), apply);
router.get('/student', roleCheck('STUDENT'), getStudentApplications);
router.get('/company', roleCheck('COMPANY'), getCompanyApplications);
router.put('/:id/status', roleCheck('COMPANY'), updateStatus);
router.put('/:id/withdraw', roleCheck('STUDENT'), withdraw);
router.post('/:applicationId/interview', roleCheck('COMPANY'), scheduleInterview);

module.exports = router;
