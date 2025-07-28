import javax.imageio.ImageIO;
import java.awt.*;
import java.io.File;
import java.io.IOException;

public class FeedbackIcon {
    public static final String correctIconPath = "./src/feedback/Correct.jpg";
    public static final String incorrectIconPath = "./src/feedback/Incorrect.jpg";
    public static final String timeoutIconPath = "./src/feedback/Timeout.jpg";

    Image correctIcon;
    Image incorrectIcon;
    Image timeoutIcon;

    public FeedbackIcon() {
        try {
            File correctFile = new File(correctIconPath);
            Image correctImage = ImageIO.read(correctFile);
            Image correctScaled = correctImage.getScaledInstance(200, 200, Image.SCALE_SMOOTH);
            this.correctIcon = correctScaled;

            File incorrectFile = new File(incorrectIconPath);
            Image incorrectImage = ImageIO.read(incorrectFile);
            Image incorrectScaled = incorrectImage.getScaledInstance(200, 200, Image.SCALE_SMOOTH);
            this.incorrectIcon = incorrectScaled;

            File timeoutFile = new File(timeoutIconPath);
            Image timeoutImage = ImageIO.read(timeoutFile);
            Image timeoutScaled = timeoutImage.getScaledInstance(200, 200, Image.SCALE_SMOOTH);
            this.timeoutIcon = timeoutScaled;
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
