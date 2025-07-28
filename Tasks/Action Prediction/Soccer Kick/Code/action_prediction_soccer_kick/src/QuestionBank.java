import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class QuestionBank {
    String name;
    List<Question> questions;
    Map<Question, Result> results;
    int correctCount;
    int incorrectCount;
    int timeoutCount;

    public QuestionBank(String n) {
        name = n;
        questions = new ArrayList<>();
        results = new HashMap<>();
    }

    public void putQuestion(Question q) {
        questions.add(q);
    }

    public Question popQuestion() {
        return questions.remove(0);
    }

    public boolean isFinish() {
        return questions.isEmpty();
    }

    public void addResult(Question q, Result result) {
        results.put(q, result);
    }

    public void calResult() {
        for (Map.Entry<Question, Result> entry : results.entrySet()) {
            switch (entry.getValue()) {
                case Correct:
                    correctCount++;
                    break;
                case InCorrect:
                    incorrectCount++;
                    break;
                default:
                    timeoutCount++;
                    break;
            }
        }
    }
}
