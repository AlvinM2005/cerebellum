import javax.swing.*;
import javax.swing.Timer;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.sql.SQLOutput;
import java.util.*;
import java.util.List;

public class Main {
    // Variables for Demo
    private static final String DEMO_IMAGE_DIR = "./src/images/demo_images/";
    private static final String DEMO_ANSWER_DIR = "./src/answers/demo_answer.txt";
    private static final String DEMO_CONDITIONS_DIR = "./src/conditions/demo_conditions.csv";
    private static final int DEMO_TOTAL_IMAGES = 5;

//    // Variables for Test1
//    private static final String TEST1_IMAGE_DIR = "./src/images/test1_images/";
//    private static final String TEST1_ANSWER_DIR = "./src/answers/test1_answer.txt";
//    private static final String TEST1_CONDITIONS_DIR = "./src/conditions/test1_conditions.csv";
//    private static final int TEST1_TOTAL_IMAGES = 96;
//
//    // Variables for Test2
//    private static final String TEST2_IMAGE_DIR = "./src/images/test2_images/";
//    private static final String TEST2_ANSWER_DIR = "./src/answers/test2_answer.txt";
//    private static final String TEST2_CONDITIONS_DIR = "./src/conditions/test2_conditions.csv";
//    private static final int TEST2_TOTAL_IMAGES = 96;

//     // Set up wait time
//     private static final int READ_TIME = 10000;
//     private static final int MAX_RESPOND_TIME = 5000;
//     private static final int FEEDBACK_TIME = 2000;

   // Wait time for test (shorter)
   private static final int READ_TIME = 100;
   private static final int MAX_RESPOND_TIME = 2000;
   private static final int FEEDBACK_TIME = 500;

   // Tasks for test (shorter)
    private static final String TEST1_IMAGE_DIR = "./src/images/test1_images_short/";
    private static final String TEST1_ANSWER_DIR = "./src/answers/test1_answer_short.txt";
    private static final String TEST1_CONDITIONS_DIR = "./src/conditions/test1_conditions_short.csv";
    private static final int TEST1_TOTAL_IMAGES = 10;
    private static final String TEST2_IMAGE_DIR = "./src/images/test2_images_short/";
    private static final String TEST2_ANSWER_DIR = "./src/answers/test2_answer_short.txt";
    private static final String TEST2_CONDITIONS_DIR = "./src/conditions/test2_conditions_short.csv";
    private static final int TEST2_TOTAL_IMAGES = 10;

    private TrialCondition currentCondition;
    private FeedbackIcon feedbackIcon;
    private Timer timer;
    private Timer feedbackTimer;
    private JLabel imageLabel;
    private List<TrialCondition> demoConditions = new ArrayList<>();
    private List<TrialCondition> test1Conditions = new ArrayList<>();
    private List<TrialCondition> test2Conditions = new ArrayList<>();
    private Map<TrialCondition, Result> results = new HashMap<>();

    // Instruction: before DEMO (1-6), before main1 (7), before main2 (8-9), after main2 (10)
    private static final String INSTRUCTION_DIR = "./src/instructions/";
    private static final int PAGE_NUM = 10;
    private List<Instruction> instructions = new ArrayList<>();

    // Instruction phase change page num
    private static final int DEMO_PAGE = 6;
    private static final int TEST1_PAGE = 7;
    private static final int TEST2_PAGE = 9;

    // Store results and calculate accuracy for each phase
    private List<Integer> demoResult = new ArrayList<>();
    private List<Integer> test1Result = new ArrayList<>();
    private List<Integer> test2Result = new ArrayList<>();
    private Integer testNum;
    private Float testAccuracy;
    private List<Float> testAccuracies = new ArrayList<>();
    private List<Integer> demoRecord = new ArrayList<>();
    private List<Integer> test1Record = new ArrayList<>();
    private List<Integer> test2Record = new ArrayList<>();
    private List<Long> demoRTs = new ArrayList<>();
    private List<Long> test1RTs = new ArrayList<>();
    private List<Long> test2RTs = new ArrayList<>();

    // Global timer (track start/end, break, RT)
    private long globalStartTime;
    private String formattedStartTime;
    private long globalEndTime;
    private String formattedEndTime;
    private long breakBegins;
    private long breakEnds;
    private long breakDurationMillis;
    private long trialStartTime;
    private long trialResponseTime;

    // Conditions csv files
    private List<String> demo_letter_name, demo_block;
    private List<Integer> demo_item_number, demo_rotation_angle, demo_mirrored;
    private List<String> test1_letter_name, test1_block;
    private List<Integer> test1_item_number, test1_rotation_angle, test1_mirrored;
    private List<String> test2_letter_name, test2_block;
    private List<Integer> test2_item_number, test2_rotation_angle, test2_mirrored;
    private static final String RESULT_DIR = "./src/results/";
    String participantInfo;

    public Main() throws IOException {
        // DEMO
        initConditions(readAnswers(DEMO_ANSWER_DIR), DEMO_IMAGE_DIR, DEMO_TOTAL_IMAGES, demoConditions);
        this.feedbackIcon = new FeedbackIcon();
        // Test1
        initConditions(readAnswers(TEST1_ANSWER_DIR), TEST1_IMAGE_DIR, TEST1_TOTAL_IMAGES, test1Conditions);
        // Test2
        initConditions(readAnswers(TEST2_ANSWER_DIR), TEST2_IMAGE_DIR, TEST2_TOTAL_IMAGES, test2Conditions);
        // Instructions
        initInstruction();
        initInfo(DEMO_CONDITIONS_DIR, "demo");
        initInfo(TEST1_CONDITIONS_DIR, "test1");
        initInfo(TEST2_CONDITIONS_DIR, "test2");
//        System.out.println("demo_letter_name: " + demo_letter_name);
//        System.out.println("demo_block: " + demo_block);
//        System.out.println("demo_item_number: " + demo_item_number);
//        System.out.println("demo_rotation_angle: " + demo_rotation_angle);
//        System.out.println("demo_mirrored: " + demo_mirrored);
//        System.out.println("test1_letter_name: " + test1_letter_name);
//        System.out.println("test1_block: " + test1_block);
//        System.out.println("test1_item_number: " + test1_item_number);
//        System.out.println("test1_rotation_angle: " + test1_rotation_angle);
//        System.out.println("test1_mirrored: " + test1_mirrored);
//        System.out.println("test2_letter_name: " + test2_letter_name);
//        System.out.println("test2_block: " + test2_block);
//        System.out.println("test2_item_number: " + test2_item_number);
//        System.out.println("test2_rotation_angle: " + test2_rotation_angle);
//        System.out.println("test2_mirrored: " + test2_mirrored);
    }

    private void initConditions(boolean[] answers, String image_dir, int image_num, List<TrialCondition> conditions) throws IOException {
        System.out.println("# of answers " + answers.length);
        if (answers.length != image_num) {
            System.out.println("# of images: " + image_num);
            throw new IllegalArgumentException("Images and answers do not match.");
        }
        for (int i = 0; i < image_num; i++) {
            int num = i + 1;
            String imgPath = image_dir + num + ".png";
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

    private void initInfo(String filepath, String whichPhase) throws IOException {
        List<String> lines = Files.readAllLines(Paths.get(filepath));

        List<String> letter_name = new ArrayList<>();
        List<String> block = new ArrayList<>();
        List<Integer> item_number = new ArrayList<>();
        List<Integer> rotation_angle = new ArrayList<>();
        List<Integer> mirrored = new ArrayList<>();

        for (int i = 1; i < lines.size(); i++) { // skip header
            String[] parts = lines.get(i).split(",");

            item_number.add(Integer.parseInt(parts[0].trim()));
            letter_name.add(parts[1].trim());
            rotation_angle.add(Integer.parseInt(parts[2].trim()));
            mirrored.add(Integer.parseInt(parts[3].trim()));
            block.add(parts[4].trim());
        }

        switch (whichPhase) {
            case "demo":
                demo_item_number = item_number;
                demo_letter_name = letter_name;
                demo_rotation_angle = rotation_angle;
                demo_mirrored = mirrored;
                demo_block = block;
                break;
            case "test1":
                test1_item_number = item_number;
                test1_letter_name = letter_name;
                test1_rotation_angle = rotation_angle;
                test1_mirrored = mirrored;
                test1_block = block;
                break;
            case "test2":
                test2_item_number = item_number;
                test2_letter_name = letter_name;
                test2_rotation_angle = rotation_angle;
                test2_mirrored = mirrored;
                test2_block = block;
                break;
            default:
                throw new IllegalArgumentException("Unknown phase: " + whichPhase);
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
        Main mainApp = new Main();
        mainApp.globalStartTime = System.currentTimeMillis();
        mainApp.formattedStartTime = getCurrentFormattedTime();
        mainApp.createUI();
    }

    private static String getCurrentFormattedTime() {
        java.text.SimpleDateFormat sdf = new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        return sdf.format(new java.util.Date());
    }

    private void createUI() {
        JFrame frame = new JFrame("Mental Rotation Test");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(1600, 1200);

        JPanel welcomePanel = new JPanel();
        welcomePanel.setLayout(new BoxLayout(welcomePanel, BoxLayout.Y_AXIS));

        JLabel instructionLabel1 = new JLabel("[For Operator] Type participant group & ID (e.g., YC_001)", SwingConstants.CENTER);
        instructionLabel1.setFont(new Font(null, Font.BOLD, 32));
        instructionLabel1.setAlignmentX(Component.CENTER_ALIGNMENT);

        JLabel instructionLabel2 = new JLabel("Press the semicolon (';') when you complete.", SwingConstants.CENTER);
        instructionLabel2.setFont(new Font(null, Font.PLAIN, 30));
        instructionLabel2.setAlignmentX(Component.CENTER_ALIGNMENT);

        JTextField inputField = new JTextField();
        inputField.setMaximumSize(new Dimension(500, 50));
        inputField.setFont(new Font(null, Font.PLAIN, 30));
        inputField.setHorizontalAlignment(SwingConstants.CENTER);

        welcomePanel.add(Box.createVerticalGlue());
        welcomePanel.add(instructionLabel1);
        welcomePanel.add(Box.createRigidArea(new Dimension(0, 20)));
        welcomePanel.add(instructionLabel2);
        welcomePanel.add(Box.createRigidArea(new Dimension(0, 40)));
        welcomePanel.add(inputField);
        welcomePanel.add(Box.createVerticalGlue());

        frame.add(welcomePanel);
        frame.setVisible(true);

        inputField.requestFocusInWindow();

        inputField.addKeyListener(new java.awt.event.KeyAdapter() {
            @Override
            public void keyTyped(java.awt.event.KeyEvent e) {
                if (e.getKeyChar() == ';') {
                    participantInfo = inputField.getText().trim();
                    System.out.println("Participant info: " + participantInfo);
                    loadInstruction(frame);
                }
            }
        });
    }

    private void loadInstruction(JFrame frame) {
        System.out.println("instruction size: " + instructions.size());
        if (instructions.isEmpty()) {
            System.out.println("(DEMO Result)" +
                    " Correct: " + demoResult.get(0) +
                    " Incorrect: " + demoResult.get(1) +
                    " Timeout: " + demoResult.get(2));
            System.out.println("(Test1 result)" +
                    " Correct: " + test1Result.get(0) +
                    " Incorrect: " + test1Result.get(1) +
                    " Timeout: " + test1Result.get(2));
            System.out.println("(Test2 result)" +
                    " Correct: " + test2Result.get(0) +
                    " Incorrect: " + test2Result.get(1) +
                    " Timeout: " + test2Result.get(2));
            printResults();
            saveResultCsv(demo_item_number, demo_letter_name, demo_rotation_angle, demo_mirrored, demo_block, demoRTs, demoRecord, "demo");
            saveResultCsv(test1_item_number, test1_letter_name, test1_rotation_angle, test1_mirrored, test1_block, test1RTs, test1Record, "test1");
            saveResultCsv(test2_item_number, test2_letter_name, test2_rotation_angle, test2_mirrored, test2_block, test2RTs, test2Record, "test2");
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
            startButton.addActionListener(e -> loadAndShowImage(frame, demoConditions));
        } else if (page == TEST1_PAGE) {
            startButton.addActionListener(e -> loadAndShowImage(frame, test1Conditions));
        } else if (page == TEST2_PAGE) {
            breakEnds = System.currentTimeMillis();
            breakDurationMillis = breakEnds - breakBegins;
            System.out.println("Break ended. Break duration: " + (breakDurationMillis / 1000) + " seconds.");
            startButton.addActionListener(e -> loadAndShowImage(frame, test2Conditions));
        } else if (page == TEST2_PAGE - 1) {
            breakBegins = System.currentTimeMillis();
            System.out.println("Break begins at: " + getCurrentFormattedTime());
            startButton.addActionListener(e -> loadInstruction(frame));
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
        frame.getContentPane().setBackground(Color.BLACK);

        imageLabel = new JLabel();
        imageLabel.setHorizontalAlignment(SwingConstants.CENTER);
        imageLabel.setBackground(Color.BLACK);
        imageLabel.setOpaque(true);

        JButton mButton = new JButton("Normal\n  V");
        JButton vButton = new JButton("Mirrored\n   M");

        JPanel buttonPanel = new JPanel();
        buttonPanel.add(mButton);
        buttonPanel.add(vButton);

        frame.setLayout(new BorderLayout());
        frame.add(imageLabel, BorderLayout.CENTER);
        frame.add(buttonPanel, BorderLayout.SOUTH);
        frame.revalidate();
        frame.repaint();

        imageLabel.setIcon(new ImageIcon(cond.image));
        trialStartTime = System.currentTimeMillis();

        timer = new Timer(MAX_RESPOND_TIME, e -> handleTimeout(frame, conditions));
        timer.setRepeats(false);
        timer.start();

        bindKeyToAction(frame, "V", "selectNormal", () -> {
            trialResponseTime = System.currentTimeMillis();
            if (timer != null && timer.isRunning()) timer.stop();
            handleV(frame, conditions);
            frame.getRootPane().getActionMap().remove("selectNormal");
            frame.getRootPane().getActionMap().remove("selectMirrored");
        });

        bindKeyToAction(frame, "M", "selectMirrored", () -> {
            trialResponseTime = System.currentTimeMillis();
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
        if (conditions == demoConditions) {
            demoResult.add(correctCount);
            demoResult.add(incorrectCount);
            demoResult.add(timeoutCount);
            testNum = DEMO_TOTAL_IMAGES;
        } else if (conditions == test1Conditions) {
            test1Result.add(correctCount);
            test1Result.add(incorrectCount);
            test1Result.add(timeoutCount);
            testNum = TEST1_TOTAL_IMAGES;
        } else if (conditions == test2Conditions) {
            test2Result.add(correctCount);
            test2Result.add(incorrectCount);
            test2Result.add(timeoutCount);
            testNum = TEST2_TOTAL_IMAGES;
        }

        testAccuracy = ((float) correctCount / testNum) * 100;
        testAccuracy = Math.round(testAccuracy * 100) / 100.0f;
        testAccuracies.add(testAccuracy);

        for (Result res : results.values()) {
            int val = (res == Result.Correct) ? 1 : 0;
            if (conditions == demoConditions) {
                demoRecord.add(val);
            } else if (conditions == test1Conditions) {
                test1Record.add(val);
            } else if (conditions == test2Conditions) {
                test2Record.add(val);
            }
        }
        results.clear();
        frame.getContentPane().removeAll();

        // Center result text
        String instruction = "";
        if (conditions == demoConditions || conditions == test1Conditions) {
            if (testAccuracy > 90.0) {
                instruction = "Try to go faster.";
            } else if (testAccuracy <= 90 && testAccuracy >= 80) {
                instruction = "Maintain speed and accuracy.";
            } else {
                instruction = "Focus on being more accurate.";
            }
        }

        String str = "<html>Correct: " + correctCount + "  Incorrect: " + incorrectCount + "  Timeout: " + timeoutCount
                + "<br>You were correct on " + testAccuracy + "% of the trials." + "<br>" + instruction;
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
        if (currentCondition.mirrored) {
            res = Result.Correct;
        } else {
            res = Result.Incorrect;
        }
        results.put(currentCondition, res);
        long reactionTime = trialResponseTime - trialStartTime;
        if (conditions == demoConditions) {
            demoRTs.add(reactionTime);
            loadDemoFeedback(frame, res);
        } else if (conditions == test1Conditions) {
            test1RTs.add(reactionTime);
            loadTestFeedback(frame, conditions);
        } else if (conditions == test2Conditions) {
            test2RTs.add(reactionTime);
            loadTestFeedback(frame, conditions);
        }
    }

    private void handleV(JFrame frame, List<TrialCondition> conditions) {
        Result res;
        if (!currentCondition.mirrored) {
            res = Result.Correct;
        } else {
            res = Result.Incorrect;
        }
        results.put(currentCondition, res);
        long reactionTime = trialResponseTime - trialStartTime;
        if (conditions == demoConditions) {
            demoRTs.add(reactionTime);
            loadDemoFeedback(frame, res);
        } else if (conditions == test1Conditions) {
            test1RTs.add(reactionTime);
            loadTestFeedback(frame, conditions);
        } else if (conditions == test2Conditions) {
            test2RTs.add(reactionTime);
            loadTestFeedback(frame, conditions);
        }
    }

    private void handleTimeout(JFrame frame, List<TrialCondition> conditions) {
        results.put(currentCondition, Result.Timeout);
        long reactionTime = MAX_RESPOND_TIME;
        if (conditions == demoConditions) {
            demoRTs.add(reactionTime);
            loadDemoFeedback(frame, Result.Timeout);
        } else if (conditions == test1Conditions) {
            test1RTs.add(reactionTime);
            loadTestFeedback(frame, conditions);
        } else if (conditions == test2Conditions) {
            test2RTs.add(reactionTime);
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
        feedbackTimer = new Timer(FEEDBACK_TIME, e -> loadAndShowImage(frame, demoConditions));
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

    private void printResults() {
        System.out.println("Result Record:");

        // Print demo
        System.out.print("Demo: ");
        for (int val : demoRecord) {
            System.out.print(val + " ");
        }
        System.out.println();

        // Print test1
        System.out.print("Test1: ");
        for (int val : test1Record) {
            System.out.print(val + " ");
        }
        System.out.println();

        // Print test2
        System.out.print("Test2: ");
        for (int val : test2Record) {
            System.out.print(val + " ");
        }
        System.out.println();

        // Testing global timer
        globalEndTime = System.currentTimeMillis();
        formattedEndTime = getCurrentFormattedTime();
        System.out.println("Start time: " + formattedStartTime);
        System.out.println("End time:   " + formattedEndTime);
    }

    private void saveResultCsv(
            List<Integer> item_numbers,
            List<String> letter_names,
            List<Integer> rotation_angles,
            List<Integer> mirrored,
            List<String> blocks,
            List<Long> RTs,
            List<Integer> correctness,
            String whichPhase
    ) {
        try {
            String filename = participantInfo + "_" + whichPhase + "_result.csv";
            java.io.FileWriter writer = new java.io.FileWriter(RESULT_DIR + filename);

            writer.write("participant_id,item_number,letter_name,rotation_angle,mirrored,block,reaction_time_ms,correct,start_time,end_time,break_duration_ms\n");

            int total = item_numbers.size();
            for (int i = 0; i < total; i++) {
                writer.write(
                        participantInfo + "," +
                                item_numbers.get(i) + "," +
                                letter_names.get(i) + "," +
                                rotation_angles.get(i) + "," +
                                mirrored.get(i) + "," +
                                blocks.get(i) + "," +
                                RTs.get(i) + "," +
                                correctness.get(i) + "," +
                                formattedStartTime + "," +
                                formattedEndTime + "," +
                                (breakDurationMillis) + "\n"
                );
            }

            writer.close();
            System.out.println("Saved to " + RESULT_DIR + filename);
        } catch (IOException e) {
            System.out.println("Failed to save result csv for " + whichPhase);
            e.printStackTrace();
        }
    }

}
