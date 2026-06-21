const express = require('express');
const router = express.Router();
const { authenticate } = require('../middleware/auth');
const { roleCheck } = require('../middleware/roleCheck');
const { getAll, getById, create, update, remove, getCompanyInternships } = require('../controllers/internshipController');

router.get('/', getAll);
router.get('/my', authenticate, roleCheck('COMPANY'), getCompanyInternships);
router.get('/:id', getById);
router.post('/', authenticate, roleCheck('COMPANY'), create);
router.put('/:id', authenticate, roleCheck('COMPANY'), update);
router.delete('/:id', authenticate, roleCheck('COMPANY'), remove);

module.exports = router;
