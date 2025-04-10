import javax.imageio.ImageIO;
import java.awt.*;
import java.io.File;
import java.io.IOException;

public class Instruction {
    String filePath;
    Image image;

    public Instruction(String imagePath) {
        try {
            File imgFile = new File(imagePath);
            Image image = ImageIO.read(imgFile);
            Image scaled = image.getScaledInstance(1516, 852, Image.SCALE_SMOOTH);
            this.filePath = imagePath;
            this.image = scaled;
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
