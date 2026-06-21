const express = require('express');
const router = express.Router();
const { authenticate } = require('../middleware/auth');
const { roleCheck } = require('../middleware/roleCheck');
const { getAll, create, update, remove } = require('../controllers/skillController');

router.get('/', getAll);
router.post('/', authenticate, roleCheck('ADMIN'), create);
router.put('/:id', authenticate, roleCheck('ADMIN'), update);
router.delete('/:id', authenticate, roleCheck('ADMIN'), remove);

module.exports = router;
