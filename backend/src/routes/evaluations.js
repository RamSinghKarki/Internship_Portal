const express = require('express');
const router = express.Router();
const { authenticate } = require('../middleware/auth');
const { createOrUpdate, getByEnrollment } = require('../controllers/evaluationController');

router.use(authenticate);

router.post('/', createOrUpdate);
router.get('/enrollment/:enrollmentId', getByEnrollment);

module.exports = router;
