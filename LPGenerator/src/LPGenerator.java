
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;

public class LPGenerator {
    float c[];
    float a1[][],a2[][],a3[][];//小于、大于、等于
    float b1[],b2[],b3[];//小于、大于、等于
    float d1[],d2[];
    private String nextLine="\r\n";
    private String lpFolder="./lpFiles/";//默认目录
    final int maxLen=200;
    public enum ExpType{
        Maximize,Minmize
    }
    public enum VarType{
        INT,FLOAT
    }
    public enum compareType{
        LessThan,MoreThan,Equal
    }
    private int varNum=-1;
    private ExpType expType;
    private VarType varType;
    int curCon=0;//生成的约束个数的计数
    public void setVariable(VarType type,int Num,float d1Mat[],float d2Mat[])
    {
        varType = type;
        varNum=Num;
        d1 = d1Mat;
        d2 = d2Mat;
    }
    public void setExpression(ExpType type,float cMat[])
    {
        expType=type;
        c=cMat;
    }
    public void setConstraints(float a1Mat[][],float a2Mat[][],float a3Mat[][],float b1Mat[],float b2Mat[],float b3Mat[])
    {
        a1=a1Mat;
        a2=a2Mat;
        a3=a3Mat;
        b1=b1Mat;
        b2=b2Mat;
        b3=b3Mat;
    }
    private void checkFolder()//检查文件储存的目录是否存在,不存在就创建
    {
        try{
            File folder=new File(lpFolder);
            if(!folder.isDirectory())
            {
                folder.mkdir();
            }
        }catch (Exception e){
            e.printStackTrace();
        }
    }
    private boolean checkMatrix()//检查系数矩阵等矩阵的形状是否正确
    {
        int i,j;
        if(c.length!=varNum) return false;//检查表达式矩阵形状
        if(a1!=null && b1!=null)//检查约束矩阵形状,其中一个为null时默认没有这种约束
        {
            if(a1.length!=b1.length) return false;
            for (i = 0; i < b1.length; i++)
            {
                if (a1[i].length != varNum) return false;
            }
        }
        if(a2!=null && b2!=null)
        {
            if(a2.length!=b2.length) return false;
            for (i = 0; i < b2.length; i++)
            {
                if (a2[i].length != varNum) return false;
            }
        }
        if(a3!=null && b3!=null)
        {
            if(a3.length!=b3.length) return false;
            for (i = 0; i < b3.length; i++)
            {
                if (a3[i].length != varNum) return false;
            }
        }
        if((d1!=null && d1.length!=varNum) || (d2!=null && d2.length!=varNum)) return false;//检查变量范围矩阵形状
        return true;
    }

    private String getExpression()//获得最优化表达式
    {
        int i,j,k;
        int curLen=0;
        StringBuilder builder=new StringBuilder("");
        StringBuilder elemBuilder=new StringBuilder("");
        for(i=0;i<c.length-1;i++)
        {
            elemBuilder.delete(0,elemBuilder.length());
            elemBuilder.append(" ").append(c[i]).append(" x_").append(i).append(" +");
            if(curLen+elemBuilder.length()>maxLen)//本行超过限制长度
            {
                builder.append(nextLine);
                builder.append(elemBuilder);
                curLen=elemBuilder.length();
            }else{
                builder.append(elemBuilder);
                curLen+=elemBuilder.length();
            }
        }
        elemBuilder.delete(0,elemBuilder.length());
        elemBuilder.append(" ").append(c[i]).append(" x_").append(i);//最后一个元素后没有+号
        if(curLen+elemBuilder.length()>maxLen)
            builder.append(nextLine).append(elemBuilder);
        else builder.append(elemBuilder);
        return builder.toString();
    }

    private String getConstraints(int n,compareType type)//获得约束表达式(小于、大于、等于)
    {
        int i;
        int curLen=0;
        boolean allZero=true;
        StringBuilder builder=new StringBuilder("");
        StringBuilder elemBuilder=new StringBuilder("");
        builder.append("_C").append(curCon).append(":");//表示约束的变量
        float a[][]=a1;
        float b[]=b1;
        switch (type){//代码复用，几种约束仅有一小部分不同
            case LessThan:a=a1;b=b1;break;
            case MoreThan:a=a2;b=b2;break;
            case Equal:a=a3;b=b3;break;
        }
        for(i=0;i<b.length-1;i++)
        {
            elemBuilder.delete(0,elemBuilder.length());
            if(a[n][i]!=0)//系数为0时该项消除
            {
                if(a[n][i]==1)
                    elemBuilder.append(" x_").append(i).append(" +");//系数为1时系数省略
                else elemBuilder.append(" ").append(a[n][i]).append(" x_").append(i).append(" +");
                allZero=false;
            }
            if(curLen+elemBuilder.length()>maxLen)
            {
                builder.append(nextLine).append(elemBuilder);
                curLen=elemBuilder.length();
            }else{
                builder.append(elemBuilder);
                curLen+=elemBuilder.length();
            }
        }
        elemBuilder.delete(0,elemBuilder.length());
        if(a[n][i]!=0)//系数为0时该项消除
        {
            if(a[n][i]==1)
                elemBuilder.append(" x_").append(i);//系数为1时系数省略
            else elemBuilder.append(" ").append(a[n][i]).append(" x_").append(i);
            allZero=false;
        }
        System.out.println(allZero);
        if(allZero) return "";//当所有的系数均为0返回空式子
        curCon++;
        switch (type)
        {
            case LessThan:elemBuilder.append(" <= ").append(b[n]);break;
            case MoreThan:elemBuilder.append(" >= ").append(b[n]);break;
            case Equal:elemBuilder.append(" == ").append(b[n]);break;
        }

        if(curLen+elemBuilder.length()>maxLen)
            builder.append(nextLine).append(elemBuilder);
        else builder.append(elemBuilder);
        return builder.toString();
    }
    private String getVariable(int n)//获得各个变量
    {
        StringBuilder builder=new StringBuilder("");
        if(d1!=null)
            builder.append(d1[n]).append(" <= ");
        builder.append("x_").append(n);
        if(d2!=null)
            builder.append(" <= ").append(d2[n]);
//        builder.append(d1[n]).append(" <= x_").append(n).append(" <= ").append(d2[n]);
        return builder.toString();
    }
    public void generateLPFile(String fileName)
    {
        if(checkMatrix()==true)
        {
            writeLPFile(fileName);
        }else{
            System.out.println("请检查输入的各个矩阵大小是否正确,生成失败");
        }
    }
    private void writeLPFile(String fileName)//开始写入lp文件,需要自行给出文件名
    {
        int i,j;
        String tmp="";
        try
        {
            checkFolder();
            File lpFile=new File(lpFolder+fileName+".lp");
            if(!lpFile.exists())
                lpFile.createNewFile();
            else{
                lpFile.delete();
                lpFile.createNewFile();
            }
            FileWriter fwriter=new FileWriter(lpFile);
            BufferedWriter bwriter=new BufferedWriter(fwriter);
            bwriter.write("\\* algorithm *\\"+nextLine);//写入算法名
            if(expType==ExpType.Maximize)//写入表达式的种类，是最小化还是最大化
                bwriter.write("Maximize"+nextLine);
            else if(expType==ExpType.Minmize)
                bwriter.write("Minimize"+nextLine);
            bwriter.write("OBJ:");//准备写最优化表达式
            bwriter.write(getExpression());
            bwriter.write(nextLine);//最优化表达式写入完成
            bwriter.write("Subject To"+nextLine);//准备写入各个约束
            if(a1!=null)
            for(i=0;i<a1.length;i++)
            {
                tmp=getConstraints(i,compareType.LessThan);
                if(tmp.length()>0)//空字符串表示该条约束无效
                {
                    bwriter.write(tmp);
                    bwriter.write(nextLine);
                }
            }
            if(a2!=null)
            for(i=0;i<a2.length;i++)
            {
                tmp=getConstraints(i,compareType.MoreThan);
                if(tmp.length()>0)
                {
                    bwriter.write(tmp);
                    bwriter.write(nextLine);
                }
            }
            if(a3!=null)
            for(i=0;i<a3.length;i++)
            {
                tmp=getConstraints(i,compareType.Equal);
                if(tmp.length()>0)
                {
                    bwriter.write(tmp);
                    bwriter.write(nextLine);
                }
            }//约束写入完成
            if(varType==VarType.INT)//准备写入变量范围
                bwriter.write("Binaries"+nextLine);
            else if(varType==VarType.FLOAT)
                bwriter.write("Bounds"+nextLine);
            for(i=0;i<varNum;i++)
                bwriter.write(getVariable(i)+nextLine);
            bwriter.write("End"+nextLine);//全部写入完毕
            bwriter.flush();
            bwriter.close();
        }catch (Exception e)
        {
            e.printStackTrace();
        }
    }
    public static void main(String args[])
    {
        LPGenerator lpGenerator=new LPGenerator();
        float c[]={3,2};
        float a[][]={{1,2},{4,5}};
        float b[]={10,20};
        float d1[]={0,0};
        float d2[]={10000,10000};
        lpGenerator.setExpression(ExpType.Maximize,c);
        lpGenerator.setConstraints(a,null,null,b,null,null);
        lpGenerator.setVariable(VarType.FLOAT,2,d1,d2);
        lpGenerator.generateLPFile("test");
    }
}
