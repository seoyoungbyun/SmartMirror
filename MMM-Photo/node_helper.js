const NodeHelper = require('node_helper');
const { parse } = require('node-html-parser');

module.exports = NodeHelper.create({
    start: function() {
        console.log('Node Helper started.');
    },

    socketNotificationReceived: function(notification, payload) {
        if (notification === 'REQUEST_PHOTO') {
            this.fetchPhoto();
        }
    },

    fetchPhoto: async function() {
        try {
            // node-fetch를 동적으로 가져오기
            const fetch = (await import('node-fetch')).default;

            // 서버에서 사진을 가져오는 요청
            const response = await fetch('http://localhost:3000/last-photo');

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            // JSON 응답을 받기
            const data = await response.json();
            console.log('서버 응답:', data);

            if (data.photo) {
                // 사진 데이터를 모듈에 전달
                this.sendSocketNotification('PHOTO_RECEIVED', data);
                console.log(data.season);
            }
        } catch (error) {
            console.error('사진 요청 실패:', error);
        }
    }
});
