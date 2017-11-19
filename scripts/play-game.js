$(document).ready(function() {
    function resetMessage() {
        var msg = $(".message");
        msg.removeClass("alert-success");
        msg.removeClass("alert-warning");
        msg.removeClass("alert-danger");
        msg.hide();
    }

    function showError(message) {
        var msg = $(".message");
        msg.addClass("alert-danger");
        msg.text(message);
        msg.show();
    }

    function showWarning(message) {
        var msg = $(".message");
        msg.addClass("alert-warning");
        msg.text(message);
        msg.show();
    }

    function showSuccess(message) {
        var msg = $(".message");
        msg.addClass("alert-success");
        msg.text(message);
        msg.show();
    }

    function verifyRedScore(score) {
        var redScore = +$(".red-score").text();
        if(redScore === score) {
            return true;
        }
        return false;
    }

    function verifyBlueScore(score) {
        var blueScore = +$(".blue-score").text();
        if(blueScore === score) {
            return true;
        }
        return false;
    }

    function incRedScore(){
        var redScoreDiv = $(".red-score");
        var redScore = +redScoreDiv.text() + 1;
        redScoreDiv.text(redScore);
        var gameLength = +redScoreDiv.data("game-length");

        if(redScore === gameLength/2) {
            redHalfTime();
        }
        else if(redScore === gameLength) {
            gameOver("Game over - Red wins!");
        }
    }

    function incBlueScore(){
        var blueScoreDiv = $(".blue-score");
        var blueScore = +blueScoreDiv.text() + 1;
        blueScoreDiv.text(blueScore);
        var gameLength = +blueScoreDiv.data("game-length");

        if(blueScore === gameLength/2) {
            blueHalfTime();
        }
        else if(blueScore === gameLength) {
            gameOver("Game over - Blue wins!");
        }
    }

    function redHalfTime() {
        var red_o = $(".btn-red-o");
        var red_d = $(".btn-red-d");

        var tempName = red_o.html();
        var tempPlayer = red_o.data("player");

        red_o.html(red_d.html());
        red_o.data("player", red_d.data("player"));

        red_d.html(tempName);
        red_d.data("player", tempPlayer);

        showWarning("Red half-time!");
    }

    function blueHalfTime() {
        var blue_o = $(".btn-blue-o");
        var blue_d = $(".btn-blue-d");

        var tempName = blue_o.html();
        var tempPlayer = blue_o.data("player");

        blue_o.html(blue_d.html());
        blue_o.data("player", blue_d.data("player"));

        blue_d.html(tempName);
        blue_d.data("player", tempPlayer);

        showWarning("Blue half-time!");
    }

    function gameOver(message) {
        showSuccess(message);
        $(".score-btn").hide();
        $(".rematch-buttons").show();
    }

    $(function() {
        Origami.fastclick(document.body);
    });

    resetMessage();

    if (verifyBlueScore(+$(".blue-score").data("game-length")))
        gameOver("Blue won this game!");
    else if (verifyRedScore(+$(".red-score").data("game-length")))
        gameOver("Red won this game!");
    else
        $(".rematch-buttons").hide();

    $(".score-btn").click(function(){
        resetMessage();

        var data = {
            game_key : $(this).data("game"),
            player_key : $(this).data("player")
        };

        if($(this).hasClass("btn-red")) {
            incRedScore();
        }
        else if($(this).hasClass("btn-blue")) {
            incBlueScore();
        }
        else {
            showError("Invalid button click");
            return;
        }

        $(".score-btn").prop("disabled", true);

        $.ajax({
            type: "POST",
            dataType : "json",
            url:"/game/play",
            data : data,
            success : function(data, textStatus) {
                if(data.success) {
                    if(!verifyBlueScore(data.blue_score)) {
                        showError("Error: Blue score does not match server score of: " + data.blue_score + ". Please refresh for most up-to-date game state");
                    }
                    else if(!verifyRedScore(data.red_score)) {
                        showError("Error: Red score does not match server score of: " + data.red_score + ". Please refresh for most up-to-date game state");
                    }
                    else {
                        $(".score-btn").prop("disabled", false);
                    }
                }
            },
            error : function(data, textStatus, errorThrown) {
                showError("Oops! Something went wrong.  Please try again.");
            }
        });
    });
});
