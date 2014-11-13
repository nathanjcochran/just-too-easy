$(document).ready(function() {
    function updateRedScore(score, percentage){
        redScore = $("#red-score");
        redScore.css("width", percentage + "%");
        redScore.text(score);
    };

    function updateBlueScore(score, percentage){
        redScore = $("#blue-score");
        redScore.css("width", percentage + "%");
        redScore.text(score);
    };

    function resetError(message) {
        var errorMsg = $(".error-message");
        errorMsg.hide();
    };

    function showError(message) {
        var errorMsg = $(".error-message");
        errorMsg.text(message);
        errorMsg.show();
    };

    function resetHalfTime(message) {
        var halfTimeMsg = $(".half-time-message");
        halfTimeMsg.hide();
    };

    function redHalfTime(message) {
        var temp = $(".red-o").text();
        $(".red-o").text($(".red-d").text());
        $(".red-d").text(temp);

        var halfTimeMsg = $(".half-time-message");
        halfTimeMsg.text(message);
        halfTimeMsg.show();
    };

    function blueHalfTime(message) {
        var temp = $(".blue-o").text();
        $(".blue-o").text($(".blue-d").text());
        $(".blue-d").text(temp);

        var halfTimeMsg = $(".half-time-message");
        halfTimeMsg.text(message);
        halfTimeMsg.show();
    };

    $(function() {
        FastClick.attach(document.body);
    });

    resetError();
    resetHalfTime();

    var gameOverMsg = $(".game-over-message");
    if(!gameOverMsg.data("game-over")) {
        gameOverMsg.hide();
    }

    $(".score-btn").click(function(){
        var data = {
            game_key : $(this).data("game"),
            player_key : $(this).data("player"),
        };

        $.ajax({
            type: "POST",
            dataType : "json",
            url:"/game/play",
            data : data,
            success : function(data, textStatus) {
                if(data.success) {
                    resetError();
                    resetHalfTime();
                    updateRedScore(data.red_score, data.red_score_percentage);
                    updateBlueScore(data.blue_score, data.blue_score_percentage);

                    if(data.half_time === "red") {
                        redHalfTime(data.message);
                    }
                    else if(data.half_time === "blue") {
                        blueHalfTime(data.message);
                    }
                    else if(data.game_over) {
                        $(".score-btn").hide();
                        $(".game-over-message").text("Game over!");
                        $(".game-over-message").show();
                    }
                }
                else {
                    showError(data.message);
                }
            },
            error : function(data, textStatus, errorThrown) {
                showError("Oops! Something went wrong.  Please try again.");
            }
        });
    });
});
