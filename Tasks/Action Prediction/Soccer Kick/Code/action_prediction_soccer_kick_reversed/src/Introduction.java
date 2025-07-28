import java.util.ArrayList;
import java.util.List;

public class Introduction {
    List<String> pageFiles;

    public Introduction(String introductionDir, int count) {
        pageFiles = new ArrayList();
        for (int i = 1; i <= count; i++) {
            pageFiles.add(introductionDir + i + ".jpg");
        }
    }

    public boolean isFinish() {
        return pageFiles.isEmpty();
    }

    public String popPage() {
        return pageFiles.remove(0);
    }
}
