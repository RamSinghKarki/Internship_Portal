const express = require('express');
const router = express.Router();
const { authenticate } = require('../middleware/auth');
const { roleCheck } = require('../middleware/roleCheck');
const { submitLog, getEnrollmentLogs, reviewLog, getMyLogs } = require('../controllers/progressController');

router.use(authenticate);

router.post('/', roleCheck('STUDENT'), submitLog);
router.get('/my', roleCheck('STUDENT'), getMyLogs);
router.get('/enrollment/:enrollmentId', getEnrollmentLogs);
router.put('/:id/review', roleCheck('INTERNAL_SUPERVISOR', 'EXTERNAL_SUPERVISOR'), reviewLog);

module.exports = router;
