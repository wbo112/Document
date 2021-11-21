package com.itheima.kerberos.test;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IOUtils;
import org.apache.hadoop.security.UserGroupInformation;

import java.io.*;
import java.lang.reflect.Array;
import java.text.SimpleDateFormat;
import java.util.Arrays;
import java.util.Date;

public class FSTools {
    private Configuration conf;
    private static FileSystem fs;

    FSTools(){
        this("nn/cdh0.itcast.cn@ITCAST.CN", "/etc/security/keytabs/nn.service.keytab");
    }

    FSTools(String principal, String keytab){
        initiali(principal, keytab);
    }

    private void initiali(String principal, String keytab){
        try{
            conf = new Configuration();
            conf.set("fs.hdfs.impl", "org.apache.hadoop.hdfs.DistributedFileSystem");
            fs = FileSystem.newInstance(conf);
            UserGroupInformation.setConfiguration(conf);
            UserGroupInformation.loginUserFromKeytab(principal, keytab);
        }catch (IOException e){
            e.printStackTrace();
        }
    }


    public void list(String path){
        try{
            Arrays.asList(fs.listStatus(new Path(path))).forEach(f -> {
                System.out.println(
                        f.getPermission().toString()+"\t"+
                                f.getReplication()+"\t"+
                                f.getLen()+"\t"+
                                new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date(f.getAccessTime())) + "\t" +
                                f.getPath().toString());
            });
        }catch (FileNotFoundException e){
            e.printStackTrace();
        }catch (IllegalArgumentException e){
            e.printStackTrace();
        }catch (IOException e){
            e.printStackTrace();
        }
    }

    public void upload(String src, String dist){
        try{
            IOUtils.copyBytes(
                    new BufferedInputStream(new FileInputStream(src)),
                    fs.create(new Path(dist), true, 65536),
                    fs.getConf(),
                    true
            );
        } catch (FileNotFoundException e){
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }catch (IllegalArgumentException e){
            e.printStackTrace();
        }
    }


    public void download(String dfsPath, String localPath){
        try{
            IOUtils.copyBytes(
                    fs.open(new Path(dfsPath)),
                    new BufferedOutputStream(new FileOutputStream(localPath)),
                    fs.getConf(),
                    true
            );
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        } catch (IllegalArgumentException e){
            e.printStackTrace();
        }
    }

    public void delete(String file){
        try{
            Path path = new Path(file);
            if (fs.exists(path)){
                System.out.println(fs.delete(path, true));
            }
        } catch (IOException e) {
            e.printStackTrace();
        } catch (IllegalArgumentException e){
            e.printStackTrace();
        }
    }

    public void cleaner() {
        try{
            fs.close();
            conf.clear();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {
        System.setProperty("java.security.krb5.conf", "/etc/krb5.conf");
        args = new String[] {"/", "/bigdata/hadoop-2.6.0-cdh5.14.4/logs/hdfs/hadoop-hdfs-namenode-cdh0.itcast.cn.log", "/nn.log", "/home/hdfs/nn.log"};
        if (args.length < 4){
            System.out.println("Usage: input parameters require is 4!");
            System.exit(1);
        }
        FSTools fsTools = new FSTools();
        System.out.println("===查询===");
        fsTools.list(args[0]);
        System.out.println("===上传===");
        fsTools.upload(args[1], args[2]);
        System.out.println("===查询===");
        fsTools.list(args[0]);
        System.out.println("===下载===");
        fsTools.download(args[2], args[3]);
        System.out.println("===删除===");
        fsTools.delete(args[2]);
        System.out.println("===查询===");
        fsTools.list(args[0]);
    }
}
