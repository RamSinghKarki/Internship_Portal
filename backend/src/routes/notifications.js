const express = require('express');
const router = express.Router();
const { authenticate } = require('../middleware/auth');
const { getAll, markRead, markAllRead, remove, getUnreadCount } = require('../controllers/notificationController');

router.use(authenticate);

router.get('/', getAll);
router.get('/unread-count', getUnreadCount);
router.put('/read-all', markAllRead);
router.put('/:id/read', markRead);
router.delete('/:id', remove);

module.exports = router;
