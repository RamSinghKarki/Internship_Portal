const express = require('express');
const router = express.Router();
const { authenticate } = require('../middleware/auth');
const { roleCheck } = require('../middleware/roleCheck');
const { upload } = require('../middleware/upload');
const {
  getProfile, updateProfile, uploadAvatar,
  getDocuments, uploadDocument, deleteDocument,
  getEnrollments, getDashboardStats,
} = require('../controllers/studentController');

router.use(authenticate, roleCheck('STUDENT'));

router.get('/profile', getProfile);
router.put('/profile', updateProfile);
router.post('/avatar', (req, res, next) => { req.uploadSubDir = 'avatars'; next(); }, upload.single('avatar'), uploadAvatar);
router.get('/documents', getDocuments);
router.post('/documents', (req, res, next) => { req.uploadSubDir = 'documents'; next(); }, upload.single('document'), uploadDocument);
router.delete('/documents/:documentId', deleteDocument);
router.get('/enrollments', getEnrollments);
router.get('/dashboard', getDashboardStats);

module.exports = router;
