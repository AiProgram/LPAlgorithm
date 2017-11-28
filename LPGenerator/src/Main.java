import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.util.Arrays;
import java.util.Random;

public class Main {
    static int MAXLINELEN = 100;//用于控制lp文件中一行的最大长度，也可以用来控制可读性
    static int origin = 0;
    static int slack = 1;
    static String nextLine = "\r\n";
    static int ROUND = 1;//由于要生成很多个相同规模的lp，所以用来区分相同规模
    static int LEN = 10000;
    static int N_sensor = 160;
    static int N_point = 800;
    static int pairNum = 20;
    static double PORTION = 0.6;
    static int Std_Check_Num = 5;
    static double Std_Check_Dis = (LEN / N_sensor) / 2 * PORTION;
    static double minDis = Std_Check_Dis / 2;
    static double maxDis = Std_Check_Dis * 2;
    static String lpFolder = "D:\\PythonProject\\Essay\\lp_files\\";
    static String valFolder = "D:\\PythonProject\\Essay\\\\val_files\\";

    static int v[] = new int[N_point];
    static double pos[] = new double[N_point];
    static double dis[] = new double[N_sensor];
    static int lBound[][] = new int[N_point][N_sensor];
    static int rBound[][] = new int[N_point][N_sensor];

    //生成各个随机数以及其他的数据
    public static void generateData() {
        int i, j, k;
        int tmp;
        Random random = new Random();
        //每个POI的价值在10和100之间
        for (i = 0; i < N_point; i++) {
            v[i] = random.nextInt(91) + 10;
            pos[i] = random.nextFloat() * LEN;
        }
        Arrays.sort(pos);
        for (i = 0; i < N_sensor; i++) {
            dis[i] = random.nextFloat() * (maxDis - minDis) + minDis;
        }
        for (i = 0; i < N_point; i++) {
            for (j = 0; j < N_sensor; j++) {
                tmp = Arrays.binarySearch(pos, pos[i] - dis[j]);
                lBound[i][j] = tmp > 0 ? tmp : (-tmp - 1);
                tmp = Arrays.binarySearch(pos, pos[i] + dis[j]);
                if (tmp > 0) {
                    rBound[i][j] = tmp;
                } else {
                    tmp = -tmp - 2;
                    if (tmp >= 0)
                        rBound[i][j] = tmp;
                    else
                        rBound[i][j] = 0;
                }
            }
        }
    }

    //记录下必要的数据
    public static void saveValue() {
        int i, j, k;
        try {
            String vFileAdress = valFolder + N_sensor + "_" + N_point + "_" + PORTION + "_" + ROUND + ".val";
            File vFile = new File(vFileAdress);
            if (!vFile.exists())
                vFile.createNewFile();
            FileWriter vWriter = new FileWriter(vFile);
            BufferedWriter writer = new BufferedWriter(vWriter);
            writer.write("N_sensor: " + N_sensor + "\r\n");
            writer.write("N_point: " + N_point + "\r\n");
            writer.write("PORTION: " + PORTION + "\r\n");
            for (i = 0; i < N_point; i++) {
                writer.write(new Double(pos[i]).toString() + " ");
            }
            writer.write("\r\n");
            for (i = 0; i < N_sensor; i++) {
                writer.write(new Double(dis[i]).toString() + " ");
            }
            writer.write("\r\n");
            for (i = 0; i < N_point; i++) {
                writer.write(new Integer(v[i]).toString() + " ");
            }
            writer.flush();
            writer.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static String getObjection()//获得整个最优化表达式
    {
        int i, j;
        StringBuilder builder = new StringBuilder();
        StringBuilder elemBuilder = new StringBuilder();//把一条语句分成许多元素
        builder.append("OBJ:");
        int curLen = builder.length();//目前这一行的长度,一行长度不能超过255
        for (i = 0; i < N_point - 1; i++)//除了最后一个元素外全部连接完成
        {
            elemBuilder.delete(0, elemBuilder.length());
            elemBuilder.append(" ").append(v[i]).append(" ").append("y_").append(i).append(" +");
            if (curLen + elemBuilder.length() + 2 <= MAXLINELEN) {
                builder.append(elemBuilder);//换行符也要占2个字符
                curLen += elemBuilder.length();
            } else {
                builder.append(nextLine).append(elemBuilder);
                curLen = elemBuilder.length();
            }
        }
        elemBuilder.delete(0, elemBuilder.length());
        elemBuilder.append(" ").append(v[N_point - 1]).append(" ").append("y_").append(N_point - 1);
        if (curLen + elemBuilder.length() + 2 <= MAXLINELEN)
            builder.append(elemBuilder);
        else
            builder.append(nextLine).append(elemBuilder);
        return builder.toString();
    }

    public static String getCons(int n,int type) {
        int i, j;
        //约束分为两部分，以0->N_sensor-1为约束2，N_sensor->N_sensor+N_point-1为约束2
        String con = "";
        StringBuilder builder = new StringBuilder();
        StringBuilder elemBuilder = new StringBuilder();
        builder.append("_C").append(n).append(":");
        int curLen = builder.length();
        if (n < N_sensor) {
            for (i = 0; i < N_point - 1; i++) {
                elemBuilder.delete(0, elemBuilder.length());
                elemBuilder.append(" ").append("x_").append(indexOfij(n, i)).append(" +");
                if (curLen + elemBuilder.length() + 2 <= MAXLINELEN) {
                    builder.append(elemBuilder);
                    curLen += elemBuilder.length();
                } else {
                    builder.append(nextLine).append(elemBuilder);
                    curLen = elemBuilder.length();
                }
            }
            elemBuilder.delete(0, elemBuilder.length());//特别处理最后一个
            elemBuilder.append(" ").append("x_").append(indexOfij(n, N_point - 1)).append(" <= 1");
            if (curLen + elemBuilder.length() + 2 <= MAXLINELEN)
                builder.append(elemBuilder);
            else
                builder.append(nextLine).append(elemBuilder);
        } else {
            n = n - N_sensor;
            for (i = 0; i < N_sensor; i++) {
                for (j = lBound[n][i]; j <= rBound[n][i]; j++) {
                    elemBuilder.delete(0, elemBuilder.length());
                    elemBuilder.append(" ").append("x_").append(indexOfij(i, j)).append(" +");
                    if (curLen + elemBuilder.length() + 2 <= MAXLINELEN) {
                        builder.append(elemBuilder);
                        curLen += elemBuilder.length();
                    } else {
                        builder.append(nextLine).append(elemBuilder);
                        curLen = elemBuilder.length();
                    }
                }
            }
            builder.delete(builder.length() - 1, builder.length());//删除最后一个多余的“+”号
            elemBuilder.delete(0, elemBuilder.length());
            elemBuilder.append("- ").append("y_").append(n).append(" >= 0");
            if (curLen + elemBuilder.length() + 2 <= MAXLINELEN)
                builder.append(elemBuilder);
            else
                builder.append(nextLine).append(elemBuilder);
        }
        return builder.toString();
    }

    public static void writeOrigin(File file) {
        int i, j, k;
        try {
            FileWriter lpWriter = new FileWriter(file);
            BufferedWriter writer = new BufferedWriter(lpWriter);
            writer.write("\\* algorithm *\\" + nextLine);
            writer.write("Maximize" + nextLine);
            writer.write(getObjection() + nextLine);//写入最优化式子
            writer.write("Subject To" + nextLine);//写入约束
            for (i = 0; i < N_point + N_sensor; i++) {
                writer.write(getCons(i,origin) + nextLine);
            }
            writer.write("Binaries" + nextLine);
            int xNum = N_point * N_sensor;
            for (i = 0; i < xNum; i++)//写入变量
            {
                writer.write("x_" + i + nextLine);
            }
            for (i = 0; i < N_point; i++) {
                writer.write("y_" + i + nextLine);
            }
            writer.write("End" + nextLine);
            writer.flush();
            writer.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static void writeSlack(File file) {
        int i, j, k;
        try {
            FileWriter lpWriter = new FileWriter(file);
            BufferedWriter writer = new BufferedWriter(lpWriter);
            writer.write("\\* algorithm *\\" + nextLine);
            writer.write("Maximize" + nextLine);
            writer.write(getObjection() + nextLine);//写入最优化式子
            writer.write("Subject To" + nextLine);//写入约束
            for (i = 0; i < N_point + N_sensor; i++) {
                writer.write(getCons(i,slack) + nextLine);
            }
            writer.write("Bounds" + nextLine);//写入变量
            int xNum = N_point * N_sensor;
            for (i = 0; i < xNum; i++) {
                writer.write("x_" + i + " <= 1" + nextLine);
            }
            for (i = 0; i < N_point; i++) {
                writer.write("-inf <= " + "y_" + i + " <= 1" + nextLine);
            }
            writer.write("End" + nextLine);
            writer.flush();
            writer.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    //写入lp文件
    public static void writeLp(int kind) {
        if (kind == origin) {
            try {
                String lpFileAdress = lpFolder + "origin" + "_" + N_sensor + "_" + N_point + "_" + PORTION + "_" + ROUND
                        + ".lp";
                File lpFile = new File(lpFileAdress);
                if (!lpFile.exists())
                    lpFile.createNewFile();
                writeOrigin(lpFile);
            } catch (Exception e) {
                e.printStackTrace();
            }
        } else if (kind == slack) {
            try {
                String lpFileAdress = lpFolder + "slack" + "_" + N_sensor + "_" + N_point + "_" + PORTION + "_" + ROUND
                        + ".lp";
                File lpFile = new File(lpFileAdress);
                if (!lpFile.exists())
                    lpFile.createNewFile();
                writeSlack(lpFile);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

    public static int indexOfij(int i, int j) {
        return i * N_point + j;
    }

    public static void main(String args[]) {
        for (int i = 1; i <= pairNum; i++) {
            ROUND = i;
            generateData();
            saveValue();
            writeLp(slack);
            //writeLp(origin);
            System.out.println("file" + ROUND + "finished");
        }
    }
}
