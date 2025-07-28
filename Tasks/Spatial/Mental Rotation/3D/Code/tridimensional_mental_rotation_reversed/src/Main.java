import javax.swing.*;
import javax.swing.Timer;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;
import java.util.List;

public class Main {
    // Variables for Demo
    private static final String DEMO_IMAGE_DIR = "./src/images/demo_images/";
    private static final String DEMO_ANSWER_DIR = "./src/answers/demo_answer.txt";
    private static final int DEMO_TOTAL_IMAGES = 5;

    // Variables for Test1
    private static final String TEST1_IMAGE_DIR = "./src/images/test1_images/";
    private static final String TEST1_ANSWER_DIR = "./src/answers/test1_answer.txt";
    private static final int TEST1_TOTAL_IMAGES = 192;

    // Variables for Test2
    private static final String TEST2_IMAGE_DIR = "./src/images/test2_images/";
    private static final String TEST2_ANSWER_DIR = "./src/answers/test2_answer.txt";
    private static final int TEST2_TOTAL_IMAGES = 192;

    // Set up wait time
    private static final int READ_TIME = 10000;
    private static final int MAX_RESPOND_TIME = 5000;
    private static final int FEEDBACK_TIME = 2000;

//    // Wait time for test (shorter)
//    private static final int READ_TIME = 100;
//    private static final int MAX_RESPOND_TIME = 2000;
//    private static final int FEEDBACK_TIME = 100;

    private TrialCondition currentCondition;
    private FeedbackIcon feedbackIcon;
    private Timer timer;
    private Timer feedbackTimer;
    private JLabel imageLabel;
    private List<TrialCondition> demo_conditions = new ArrayList<>();
    private List<TrialCondition> test1_conditions = new ArrayList<>();
    private List<TrialCondition> test2_conditions = new ArrayList<>();
    private Map<TrialCondition, Result> results = new HashMap<>();

    // Instruction: before DEMO (1-5), before main1 (6), before main2 (7-8), after main2 (9)
    private static final String INSTRUCTION_DIR = "./src/instructions/";
    private static final int PAGE_NUM = 9;
    private List<Instruction> instructions = new ArrayList<>();
    // Instruction phase change page num
    private static final int DEMO_PAGE = 5;
    private static final int TEST1_PAGE = 6;
    private static final int TEST2_PAGE = 8;

    // Store results for each phase
    private List<Integer> demo_result = new ArrayList<>();
    private List<Integer> test1_result = new ArrayList<>();
    private List<Integer> test2_result = new ArrayList<>();

    public Main() throws IOException {
        // DEMO
        initConditions(readAnswers(DEMO_ANSWER_DIR), DEMO_IMAGE_DIR, DEMO_TOTAL_IMAGES, demo_conditions);
        this.feedbackIcon = new FeedbackIcon();
        // Test1
        initConditions(readAnswers(TEST1_ANSWER_DIR), TEST1_IMAGE_DIR, TEST1_TOTAL_IMAGES, test1_conditions);
        // Test2
        initConditions(readAnswers(TEST2_ANSWER_DIR), TEST2_IMAGE_DIR, TEST2_TOTAL_IMAGES, test2_conditions);
        // Instructions
        initInstruction();
    }

    private void initConditions(boolean[] answers, String image_dir, int image_num, List<TrialCondition> conditions) throws IOException {
        System.out.println("# of answers " + answers.length);
        if (answers.length != image_num) {
            System.out.println("# of images: " + image_num);
            throw new IllegalArgumentException("Images and answers do not match.");
        }
        for (int i = 0; i < image_num; i++) {
            int num = i + 1;
            String imgPath = image_dir + num + ".jpg";
            TrialCondition cond = new TrialCondition(imgPath, answers[i]);
            conditions.add(cond);
        }
        Collections.shuffle(conditions);
    }

    private void initInstruction() throws IOException {
        System.out.println("# of instruction pages " + PAGE_NUM);
        for (int i = 0; i < PAGE_NUM; i++) {
            int num = i + 1;
            String imgPath = INSTRUCTION_DIR + num + ".png";
            Instruction ins = new Instruction(imgPath);
            instructions.add(ins);
        }
    }

    private boolean[] readAnswers(String answer_dir) throws IOException {
        List<Boolean> list = new ArrayList<>();
        for (String line : Files.readAllLines(Paths.get(answer_dir))) {
            line = line.trim();
            System.out.println(line);
            if (line.isEmpty()) continue;
            switch (line) {
                case "0":
                    list.add(false);
                    System.out.println(line + ", add false");
                    break;
                case "1":
                    list.add(true);
                    System.out.println(line + ", add true");
                    break;
            }
        }
        System.out.println(list);
        boolean[] answers = new boolean[list.size()];
        for (int i = 0; i < list.size(); i++) {
            answers[i] = list.get(i);
        }
        for (boolean answer : answers) {
            System.out.print(answer + " ");
        }
        System.out.println();
        return answers;
    }

    // Meta-method for key binding (actionName is used to differentiate functions of distinct keys, make sure it is different for every bindings)
    private void bindKeyToAction(JFrame frame, String keyStrokeStr, String actionName, Runnable action) {
        JRootPane rootPane = frame.getRootPane();
        InputMap inputMap = rootPane.getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW);
        ActionMap actionMap = rootPane.getActionMap();

        inputMap.put(KeyStroke.getKeyStroke(keyStrokeStr), actionName);
        actionMap.put(actionName, new AbstractAction() {
            @Override
            public void actionPerformed(ActionEvent e) {
                action.run();
            }
        });
    }

    public static void main(String[] args) throws IOException {
        new Main().createUI();
    }

    private void createUI() {
        JFrame frame = new JFrame("Test");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(1600, 1200);

        JPanel welcomePanel = new JPanel(new BorderLayout());
        JLabel welcomeLabel = new JLabel("Are you ready?", SwingConstants.CENTER);
        welcomeLabel.setFont(new Font(null, Font.PLAIN, 36));
        JButton startButton = new JButton("Start");
        startButton.addActionListener(e -> loadInstruction(frame));

        welcomePanel.add(welcomeLabel, BorderLayout.CENTER);
        welcomePanel.add(startButton, BorderLayout.SOUTH);

        frame.add(welcomePanel);
        frame.setVisible(true);
    }

    private void loadInstruction(JFrame frame) {
        System.out.println("instruction size: " + instructions.size());
        if (instructions.isEmpty()) {
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

        frame.getContentPane().removeAll();
        imageLabel = new JLabel();
        imageLabel.setHorizontalAlignment(SwingConstants.CENTER);

        JButton startButton = new JButton("Next");
        startButton.setEnabled(false);

        frame.setLayout(new BorderLayout());
        frame.add(imageLabel, BorderLayout.CENTER);
        frame.add(startButton, BorderLayout.SOUTH);
        frame.revalidate();
        frame.repaint();

        Instruction ins = instructions.remove(0);
        imageLabel.setIcon(new ImageIcon(ins.image));

        bindKeyToAction(frame, "SPACE", "nextInstruction_", () -> startButton.doClick());

        Timer unlockTimer = new Timer(READ_TIME, e -> {
            startButton.setEnabled(true);
        });
        unlockTimer.setRepeats(false);
        unlockTimer.start();

        int page = PAGE_NUM - instructions.size();
        System.out.println("Now on instruction page: " + page);

        if (page == DEMO_PAGE) {
            startButton.addActionListener(e -> loadAndShowImage(frame, demo_conditions));
        } else if (page == TEST1_PAGE) {
            startButton.addActionListener(e -> loadAndShowImage(frame, test1_conditions));
        } else if (page == TEST2_PAGE) {
            startButton.addActionListener(e -> loadAndShowImage(frame, test2_conditions));
        } else {
            startButton.addActionListener(e -> loadInstruction(frame));
        }

    }

    private void loadAndShowImage(JFrame frame, List<TrialCondition> conditions) {
        System.out.println("conditions size: " + conditions.size());
        frame.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).remove(KeyStroke.getKeyStroke("SPACE"));
        frame.getRootPane().getActionMap().remove("goToNextTask");
        frame.getRootPane().getActionMap().remove("startInstruction");

        if (timer != null) {
            timer.stop();
        }

        if (conditions.isEmpty()) {
            showResults(frame, conditions);
            return;
        }
        TrialCondition cond = conditions.remove(0);
        this.currentCondition = cond;

        frame.getContentPane().removeAll();
        imageLabel = new JLabel();
        imageLabel.setHorizontalAlignment(SwingConstants.CENTER);

        JButton mButton = new JButton("Normal\n  M");
        JButton vButton = new JButton("Mirrored\n   V");

        JPanel buttonPanel = new JPanel();
        buttonPanel.add(mButton);
        buttonPanel.add(vButton);

        frame.setLayout(new BorderLayout());
        frame.add(imageLabel, BorderLayout.CENTER);
        frame.add(buttonPanel, BorderLayout.SOUTH);
        frame.revalidate();
        frame.repaint();

        imageLabel.setIcon(new ImageIcon(cond.image));

        timer = new Timer(MAX_RESPOND_TIME, e -> handleTimeout(frame, conditions));
        timer.setRepeats(false);
        timer.start();

        bindKeyToAction(frame, "V", "selectNormal", () -> {
            if (timer != null && timer.isRunning()) timer.stop();
            handleV(frame, conditions);
            frame.getRootPane().getActionMap().remove("selectNormal");
            frame.getRootPane().getActionMap().remove("selectMirrored");
        });

        bindKeyToAction(frame, "M", "selectMirrored", () -> {
            if (timer != null && timer.isRunning()) timer.stop();
            handleM(frame, conditions);
            frame.getRootPane().getActionMap().remove("selectNormal");
            frame.getRootPane().getActionMap().remove("selectMirrored");
        });
    }

    private void showResults(JFrame frame, List<TrialCondition> conditions) {
        System.out.println("show result");
        int correctCount = 0, incorrectCount = 0, timeoutCount = 0;
        Set<Map.Entry<TrialCondition, Result>> entries = results.entrySet();
        for (Map.Entry<TrialCondition, Result> entry : entries) {
            Result res = entry.getValue();
            if (res == Result.Correct) {
                correctCount++;
            } else if (res == Result.Incorrect) {
                incorrectCount++;
            } else {
                timeoutCount++;
            }
        }

        System.out.println("Correct: " + correctCount + " Incorrect: " + incorrectCount + " Timeout: " + timeoutCount);
        if (conditions == demo_conditions) {
            demo_result.add(correctCount);
            demo_result.add(incorrectCount);
            demo_result.add(timeoutCount);
        } else if (conditions == test1_conditions) {
            test1_result.add(correctCount);
            test1_result.add(incorrectCount);
            test1_result.add(timeoutCount);
        } else if (conditions == test2_conditions) {
            test2_result.add(correctCount);
            test2_result.add(incorrectCount);
            test2_result.add(timeoutCount);
        }

        results.clear();
        frame.getContentPane().removeAll();

        // Center result text
        String str = "Correct: " + correctCount + "  Incorrect: " + incorrectCount + "  Timeout: " + timeoutCount;
        JLabel resultLabel = new JLabel(str, SwingConstants.CENTER);
        resultLabel.setFont(new Font(null, Font.PLAIN, 36));

        // Add Start button
        JButton startButton = new JButton("Start Next Phase");
        startButton.setFont(new Font(null, Font.PLAIN, 24));
        bindKeyToAction(frame, "SPACE", "goToNextTask", () -> startButton.doClick());
        startButton.addActionListener(e -> loadInstruction(frame));

        // Layout
        JPanel resultPanel = new JPanel(new BorderLayout());
        resultPanel.add(resultLabel, BorderLayout.CENTER);
        resultPanel.add(startButton, BorderLayout.SOUTH);

        frame.setLayout(new BorderLayout());
        frame.add(resultPanel, BorderLayout.CENTER);
        frame.revalidate();
        frame.repaint();
    }

    private void handleM(JFrame frame, List<TrialCondition> conditions) {
        Result res;
        if (!currentCondition.mirrored) {
            res = Result.Correct;
        } else {
            res = Result.Incorrect;
        }
        results.put(currentCondition, res);
        if (conditions == demo_conditions) {
            loadDemoFeedback(frame, res);
        } else {
            loadTestFeedback(frame, conditions);
        }
    }

    private void handleV(JFrame frame, List<TrialCondition> conditions) {
        Result res;
        if (currentCondition.mirrored) {
            res = Result.Correct;
        } else {
            res = Result.Incorrect;
        }
        results.put(currentCondition, res);
        if (conditions == demo_conditions) {
            loadDemoFeedback(frame, res);
        } else {
            loadTestFeedback(frame, conditions);
        }
    }

    private void handleTimeout(JFrame frame, List<TrialCondition> conditions) {
        results.put(currentCondition, Result.Timeout);
        if (conditions == demo_conditions) {
            loadDemoFeedback(frame, Result.Timeout);
        } else {
            loadTestFeedback(frame, conditions);
        }
    }

    private void loadDemoFeedback(JFrame frame, Result res) {
        frame.getContentPane().removeAll();
        imageLabel = new JLabel();
        imageLabel.setHorizontalAlignment(SwingConstants.CENTER);

        frame.setLayout(new BorderLayout());
        frame.add(imageLabel, BorderLayout.CENTER);
        frame.revalidate();
        frame.repaint();

        Image feedbackImage;
        switch (res) {
            case Correct:
                feedbackImage = feedbackIcon.correctIcon;
                break;
            case Incorrect:
                feedbackImage = feedbackIcon.incorrectIcon;
                break;
            case Timeout:
                feedbackImage = feedbackIcon.timeoutIcon;
                break;
            default:
                throw new IllegalStateException("Unexpected value: " + res);
        }
        imageLabel.setIcon(new ImageIcon(feedbackImage));
        if (feedbackTimer != null) {
            feedbackTimer.stop();
        }
        feedbackTimer = new Timer(FEEDBACK_TIME, e -> loadAndShowImage(frame, demo_conditions));
        feedbackTimer.setRepeats(false);
        feedbackTimer.start();
    }

    private void loadTestFeedback(JFrame frame, List<TrialCondition> conditions) {
        frame.getContentPane().removeAll();
        imageLabel = new JLabel();
        imageLabel.setHorizontalAlignment(SwingConstants.CENTER);

        frame.setLayout(new BorderLayout());
        frame.add(imageLabel, BorderLayout.CENTER);
        frame.revalidate();
        frame.repaint();

        if (feedbackTimer != null) {
            feedbackTimer.stop();
        }
        feedbackTimer = new Timer(FEEDBACK_TIME, e -> loadAndShowImage(frame, conditions));
        feedbackTimer.setRepeats(false);
        feedbackTimer.start();
    }

}
