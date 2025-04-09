import javax.imageio.ImageIO;
import javax.swing.*;
import java.awt.*;
import java.io.File;
import java.io.IOException;
import java.util.Random;

public class TrialCondition {
    String filePath;
    Image image;
    boolean mirrored;

    public TrialCondition(String imagePath, boolean mirrored) {
        try {
            File imgFile = new File(imagePath);
            Image image = ImageIO.read(imgFile);
            Image scaled = image.getScaledInstance(400, 400, Image.SCALE_SMOOTH);
            this.filePath = imagePath;
            this.image = scaled;
            this.mirrored = mirrored;
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
