const express = require('express');
const multer = require('multer');
const path = require('path');
const app = express();
const PORT = 3000;

// Multer 설정
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, path.join('/home/mirror/Public/uploads')); // 파일 저장 위치
    },
    filename: function (req, file, cb) {
        cb(null, file.originalname); // 파일 이름 설정
    }
});

const upload = multer({ storage: storage });

// 정적 파일 서비스 - Public 디렉터리를 지정
app.use(express.static(path.join('/home/mirror/Public')));

// 마지막 업로드된 사진 경로와 메타데이터를 저장하는 변수
let lastUploadedPhoto = null;

// 사진 업로드 라우트
app.post('/upload', upload.single('photo'), (req, res) => {
    if (req.file) {
        lastUploadedPhoto = {
            photo: `/uploads/${req.file.filename}`,
            season: req.body.season,
            mood: req.body.mood
        };
        // 업로드 후 경로와 추가 데이터를 JSON으로 응답
        res.json(lastUploadedPhoto);
    } else {
        res.status(400).json({ error: '사진 업로드 실패' });
    }
});

// 마지막 업로드된 사진을 반환하는 라우트
app.get('/last-photo', (req, res) => {
    if (lastUploadedPhoto) {
        res.json(lastUploadedPhoto);
    } else {
        res.status(404).json({ error: '사진이 없습니다' });
    }
});

// 서버 실행
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});

