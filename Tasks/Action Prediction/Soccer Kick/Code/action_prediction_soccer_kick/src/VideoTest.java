import javafx.animation.KeyFrame;
import javafx.animation.Timeline;
import javafx.application.Application;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.input.KeyCode;
import javafx.scene.input.KeyEvent;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import javafx.scene.media.MediaException;
import javafx.scene.media.MediaView;
import javafx.stage.Stage;
import javafx.util.Duration;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;

import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.media.Media;
import javafx.scene.media.MediaPlayer;
import java.io.File;
import java.util.Objects;

public class VideoTest extends Application {

    // general
    private static final int SCENE_WIDTH = 1600;
    private static final int SCENE_HEIGHT = 1200;
    private boolean hasResponded = false;

    // introduction pages
    private static final int INTRODUCTION_IMAGE_COUNT = 10;
    private static final int DEMO_PAGE = 5;
    private static final int TEST1_PAGE = 6;
    private static final int TEST2_PAGE = 8;
    private static final String INTRODUCTION_IMAGE_DIR = "./src/introduction_images/";
    Introduction introduction;

    // demo
    private static final int DEMO_QUESTION_COUNT = 6;
    private static final String DEMO_VIDEO_DIR = "./src/videos/demo/";
    private static final String DEMO_ANSWER_FILE = "./src/answers/demo_answer.txt";
    private static final String DEMO_NAME = "DEMO";
    private static final ArrayList<Integer> demo_result = new ArrayList<>();
    QuestionBank demoQuestionBank;

    // test1
    private static final int TEST1_QUESTION_COUNT = 6;
    private static final String TEST1_VIDEO_DIR = "./src/videos/test1/";
    private static final String TEST1_ANSWER_FILE = "./src/answers/test1_answer.txt";
    private static final String TEST1_NAME = "TEST1";
    private static final ArrayList<Integer> test1_result = new ArrayList<>();
    QuestionBank test1QuestionBank;

    // test2
    private static final int TEST2_QUESTION_COUNT = 6;
    private static final String TEST2_VIDEO_DIR = "./src/videos/test2/";
    private static final String TEST2_ANSWER_FILE = "./src/answers/test2_answer.txt";
    private static final String TEST2_NAME = "TEST2";
    private static final ArrayList<Integer> test2_result = new ArrayList<>();
    QuestionBank test2QuestionBank;

    // Set up wait time
    private static final int READ_TIME = 10000;
    private static final int MAX_RESPOND_TIME = 5000;
    private static final int FEEDBACK_TIME = 2000;

//    // Shorter wait time for test
//    private static final int READ_TIME = 100;
//    private static final int MAX_RESPOND_TIME = 2000;
//    private static final int FEEDBACK_TIME = 500;

    @Override
    public void start(Stage primaryStage) throws Exception {
        initQuestionBanks();
        introduction = new Introduction(INTRODUCTION_IMAGE_DIR, INTRODUCTION_IMAGE_COUNT);
        VBox primaryLayout = new VBox(20);
        Scene prymryScene = new Scene(primaryLayout, SCENE_WIDTH, SCENE_HEIGHT);
        primaryStage.setScene(prymryScene);
        primaryStage.show();
        loadIntroductionPage(primaryStage);
    }

    private void initQuestionBanks() {
        this.demoQuestionBank = initQuestionBank(DEMO_NAME, DEMO_VIDEO_DIR, DEMO_QUESTION_COUNT, DEMO_ANSWER_FILE);
        this.test1QuestionBank = initQuestionBank(TEST1_NAME, TEST1_VIDEO_DIR, TEST1_QUESTION_COUNT, TEST1_ANSWER_FILE);
        this.test2QuestionBank = initQuestionBank(TEST2_NAME, TEST2_VIDEO_DIR, TEST2_QUESTION_COUNT, TEST2_ANSWER_FILE);
    }

    private QuestionBank initQuestionBank(String name, String videoDir, int videoCount, String answerDir) {
        QuestionBank qb = new QuestionBank(name);
        boolean[] qAnswers = loadAnswer(answerDir, videoCount);
        for (int i = 0; i < videoCount; i++) {
            Question q = new Question(videoDir + (i + 1) + ".mp4", qAnswers[i]);
            qb.putQuestion(q);
        }
        Collections.shuffle(qb.questions);
        return qb;
    }

    private void loadIntroductionPage(Stage stage) {
        if (introduction.isFinish()) {
            System.out.println("(DEMO Result)" +
                    " Correct: " + demo_result.get(0) +
                    " Incorrect: " + demo_result.get(1) +
                    " Timeout: " + demo_result.get(2));
            System.out.println("(Test1 result)" +
                    " Correct: " + test1_result.get(0) +
                    " Incorrect: " + test1_result.get(1) +
                    " Timeout: " + test1_result.get(2));
            System.out.println("(Test2 result)" +
                    " Correct: " + test2_result.get(0) +
                    " Incorrect: " + test2_result.get(1) +
                    " Timeout: " + test2_result.get(2));
            System.exit(0);
        }

        String page = introduction.popPage();
        System.out.println("Introduction: " + page);
        Image image = new Image(new File(page).toURI().toString());
        ImageView imageView = new ImageView(image);
        imageView.setPreserveRatio(true);
        imageView.setFitWidth(SCENE_WIDTH * 0.8);

        Button nextButton = new Button("Next");
        nextButton.setDisable(true);

        Timeline timeline = new Timeline(new KeyFrame(Duration.millis(READ_TIME), e -> nextButton.setDisable(false)));
        timeline.play();

        nextButton.setOnAction(e -> {
            loadIntroductionPage(stage);
        });

        VBox imageLayout = new VBox(20);
        imageLayout.setAlignment(Pos.CENTER);
        imageLayout.getChildren().addAll(imageView, nextButton);

        Scene imageScene = new Scene(imageLayout, SCENE_WIDTH, SCENE_HEIGHT);
        stage.setScene(imageScene);

        int pageNum = INTRODUCTION_IMAGE_COUNT - introduction.pageFiles.size();
        System.out.println("Now on instruction page: " + pageNum);

        if (pageNum == DEMO_PAGE) {
            nextButton.setOnAction(e -> loadQuestionPage(stage, demoQuestionBank));
        } else if (pageNum == TEST1_PAGE) {
            nextButton.setOnAction(e -> loadQuestionPage(stage, test1QuestionBank));
        } else if (pageNum == TEST2_PAGE) {
            nextButton.setOnAction(e -> loadQuestionPage(stage, test2QuestionBank));
        } else {
            nextButton.setOnAction(e -> loadIntroductionPage(stage));
        }
    }

    private void loadQuestionPage(Stage stage, QuestionBank qb) {
        hasResponded = false;

        if (qb.isFinish()) {
            loadResultPage(stage, qb);
            return;
        }
        Question q = qb.popQuestion();
        System.out.println("next video is" + q.videoDir);
        Media media = new Media(new File(q.videoDir).toURI().toString());
        MediaPlayer mediaPlayer = new MediaPlayer(media);
        MediaView mediaView = new MediaView(mediaPlayer);

        Button mButton = new Button("Left (L)");
        mButton.setDefaultButton(false);
        mButton.setDisable(true);
        mButton.setFocusTraversable(false);
        Button vButton = new Button("Right (R)");
        vButton.setDefaultButton(false);
        vButton.setDisable(true);
        vButton.setFocusTraversable(false);

        Timeline timeoutTimeline = new Timeline(new KeyFrame(Duration.millis(MAX_RESPOND_TIME), e -> {
            System.out.println("timeout event");
            if (!hasResponded) {
                handleTimeout(stage, qb, q);
            }
        }));
        timeoutTimeline.setCycleCount(1);

        mediaPlayer.setOnError(new Runnable() {
            @Override
            public void run() {
                MediaException error = mediaPlayer.getError();
                System.out.println(q.videoDir + " play error: " + error);
                System.out.println(q.videoDir + " play error: " + error);
                handleAsCorrect(stage, qb, q);
            }
        });

        mediaPlayer.setOnEndOfMedia(() -> {
            System.out.println(q.videoDir + " finish display event");
            mButton.setDisable(false);
            vButton.setDisable(false);
            timeoutTimeline.play();
        });

        mButton.setOnAction(e -> {
            timeoutTimeline.stop();
            if (!hasResponded) {
                hasResponded = true;
                handleM(stage, qb, q, timeoutTimeline);
            }
            mButton.setDisable(true);
            vButton.setDisable(true);
        });

        vButton.setOnAction(e -> {
            timeoutTimeline.stop();
            if (!hasResponded) {
                hasResponded = true;
                handleV(stage, qb, q, timeoutTimeline);
            }
            mButton.setDisable(true);
            vButton.setDisable(true);
        });

        HBox buttonBox = new HBox(20);
        buttonBox.setAlignment(Pos.CENTER);
        buttonBox.getChildren().addAll(mButton, vButton);

        VBox questionLayout = new VBox(20);
        questionLayout.setAlignment(Pos.CENTER);
        questionLayout.getChildren().addAll(mediaView, buttonBox);

        Scene questionScene = new Scene(questionLayout, SCENE_WIDTH, SCENE_HEIGHT);
        questionScene.addEventHandler(KeyEvent.KEY_PRESSED, event -> {
            if (event.getCode() == KeyCode.M) {
                if (!hasResponded) {
                    handleM(stage, qb, q, timeoutTimeline);
                    event.consume();
                } else {
                    event.consume();
                }
            } else if (event.getCode() == KeyCode.V) {
                if (!hasResponded) {
                    handleV(stage, qb, q, timeoutTimeline);
                    event.consume();
                } else {
                    event.consume();
                }
            } else {
                event.consume();
            }
        });

        stage.setScene(questionScene);
        System.out.println(q.videoDir + " start play");
        System.out.println(q.videoDir + " media: " + media);
        mediaPlayer.play();
    }

    private void handleM(Stage stage, QuestionBank qb, Question q, Timeline timeoutTimeLine) {
        timeoutTimeLine.stop();
        Result r;
        if (q.answer) {
            r = Result.Correct;
        } else {
            r = Result.InCorrect;
        }
        loadFeedbackPage(stage, qb, q, r);
    }

    private void handleV(Stage stage, QuestionBank qb, Question q, Timeline timeoutTimeLine) {
        timeoutTimeLine.stop();
        Result r;
        if (!q.answer) {
            r = Result.Correct;
        } else {
            r = Result.InCorrect;
        }
        loadFeedbackPage(stage, qb, q, r);
    }

    private void handleTimeout(Stage stage, QuestionBank qb, Question q) {
        if (!hasResponded) {
            loadFeedbackPage(stage, qb, q, Result.Timeout);
        }
    }

    private void handleAsCorrect(Stage stage, QuestionBank qb, Question q) {
        loadFeedbackPage(stage, qb, q, Result.Correct);
    }

    private void loadFeedbackPage(Stage stage, QuestionBank qb, Question q, Result result) {
        qb.addResult(q, result);
        if (qb.name.equals(DEMO_NAME)) {
            String feedbackIconDir;
            switch (result) {
                case Correct:
                    feedbackIconDir = FeedbackIcon.correctIconPath;
                    break;
                case InCorrect:
                    feedbackIconDir = FeedbackIcon.incorrectIconPath;
                    break;
                default:
                    feedbackIconDir = FeedbackIcon.timeoutIconPath;
                    break;
            }
            Image image = new Image(new File(feedbackIconDir).toURI().toString());
            ImageView imageView = new ImageView(image);
            imageView.setPreserveRatio(true);
            imageView.setFitWidth(200);

            VBox imageLayout = new VBox(20);
            imageLayout.setAlignment(Pos.CENTER);
            imageLayout.getChildren().addAll(imageView);

            Scene imageScene = new Scene(imageLayout, SCENE_WIDTH, SCENE_HEIGHT);
            stage.setScene(imageScene);

            Timeline timeline = new Timeline(new KeyFrame(Duration.millis(FEEDBACK_TIME), e -> {
                loadQuestionPage(stage, qb);
            }));
            timeline.play();
        } else {
            Label messageLabel = new Label(" ");
            VBox whiteLayout = new VBox(20);
            whiteLayout.setAlignment(Pos.CENTER);
            whiteLayout.getChildren().add(messageLabel);

            Scene whiteScene = new Scene(whiteLayout, SCENE_WIDTH, SCENE_HEIGHT);
            stage.setScene(whiteScene);

            Timeline timeline = new Timeline(new KeyFrame(Duration.millis(FEEDBACK_TIME), e -> {
                loadQuestionPage(stage, qb);
            }));
            timeline.play();
        }
    }

    private void loadResultPage(Stage stage, QuestionBank qb) {
        qb.calResult();
        if (Objects.equals(qb.name, DEMO_NAME)) {
            demo_result.add(qb.correctCount);
            demo_result.add(qb.incorrectCount);
            demo_result.add(qb.timeoutCount);
        } else if (Objects.equals(qb.name, TEST1_NAME)) {
            test1_result.add(qb.correctCount);
            test1_result.add(qb.incorrectCount);
            test1_result.add(qb.timeoutCount);
        } else if (Objects.equals(qb.name, TEST2_NAME)) {
            test2_result.add(qb.correctCount);
            test2_result.add(qb.incorrectCount);
            test2_result.add(qb.timeoutCount);
        }
        Label resultLabel = new Label("Correct: " + qb.correctCount + ", Wrong: " + qb.incorrectCount + ", Timeout: " + qb.timeoutCount);
        VBox resultLayout = new VBox(20);
        Button nextButton = new Button("Next");
        nextButton.setOnAction(e -> loadIntroductionPage(stage));
        resultLayout.setAlignment(Pos.CENTER);
        resultLayout.getChildren().addAll(resultLabel, nextButton);

        Scene resultScene = new Scene(resultLayout, SCENE_WIDTH, SCENE_HEIGHT);
        stage.setScene(resultScene);
    }

    private boolean[] loadAnswer(String answerDir, int videoCount) {
        boolean[] buffer = new boolean[videoCount];
        int i = 0;
        try (BufferedReader br = new BufferedReader(new FileReader(answerDir))) {
            String line;
            while ((line = br.readLine()) != null) {
                buffer[i++] = line.equals("1");
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        return buffer;
    }

    public static void main(String[] args) {
        launch(args);
    }
}
