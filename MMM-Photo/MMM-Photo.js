Module.register("MMM-Photo", {
    defaults: {
        message: "사진을 전송 후 눌러주세요."
    },

    start: function() {
        this.photo = null;
        this.season = '';
        this.mood = '';
        this.photoSent = false;
    },

    getDom: function() {
        var wrapper = document.createElement("div");
        console.log("확인");

        // "사진전송" 버튼은 항상 표시합니다.
        var button = document.createElement("button");
        button.innerHTML = "사진전송완료";
        button.className = "photo-button";
        button.addEventListener("click", () => {
            this.sendSocketNotification("REQUEST_PHOTO");
        });

        wrapper.appendChild(button);

        return wrapper;
    },

    socketNotificationReceived: function(notification, payload) {
        if (notification === "PHOTO_RECEIVED") {
            this.photo = payload.photo;
            this.season = payload.season;
            this.mood = payload.mood;
            this.updateDom();
            this.receiveSelection(this.season, this.mood); // 계절과 분위기 알림 표시
        }
    },

    getStyles: function() {
        return ["MMM-Photo.css"];
    },

    receiveSelection: function(season, mood) {
        this.sendNotification("SHOW_ALERT", {type: "notification", message: "계절: " + season + "\n분위기: " + mood});
        this.updateDom();
    }
});