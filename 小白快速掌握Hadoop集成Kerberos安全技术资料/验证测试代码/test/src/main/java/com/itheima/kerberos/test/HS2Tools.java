package com.itheima.kerberos.test;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.security.UserGroupInformation;

import java.io.IOException;
import java.sql.*;

public class HS2Tools {
    private static String driverName = "org.apache.hive.jdbc.HiveDriver";
    private static String url = "jdbc:hive2://cdh0.itcast.cn:10000/default;principal=hive/cdh0.itcast.cn@ITCAST.CN";
    private static ResultSet res;

    public static Connection getConnection() {
        Configuration conf = new Configuration();
        try{
            UserGroupInformation.setConfiguration(conf);
            UserGroupInformation.loginUserFromKeytab("hive/cdh0.itcast.cn@ITCAST.CN", "/etc/security/keytabs/hive.keytab");
        } catch (IOException e){
            e.printStackTrace();
        }
        try{
            Class.forName(driverName);
            return DriverManager.getConnection(url);
        }catch (ClassNotFoundException e){
            e.printStackTrace();
        }catch (SQLException e){
            e.printStackTrace();
        }
        return null;
    }

    public void showTables(Statement statement) {
        try{
            ResultSet res = statement.executeQuery("SHOW TABLES");
            while (res.next()){
                System.out.println(res.getString(1));
            }
        }catch (SQLException e){
            e.printStackTrace();
        }
    }

    public void descTable(Statement statement, String tableName) {
        try {
            res = statement.executeQuery("DESCRIBE " + tableName);
            while (res.next()){
                System.out.println(res.getString(1) + "\t" + res.getString(2));
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    public void dropTable(Statement statement, String tableName){
        try {
            statement.execute("DROP TABLE IF EXISTS " + tableName);
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    public void queryData(Statement statement, String tableName) {
        try {
            res = statement.executeQuery("SELECT * FROM " + tableName + " LIMIT 20");
            while (res.next()){
                System.out.println(res.getString(1) + "," + res.getString(2) + "," + res.getString(3));
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    public void createTable(Statement statement, String tableName) {
        try {
            statement.execute("CREATE TABLE "  + tableName + " AS SELECT * FROM test_temp");
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) throws Exception{
//        System.setProperty("java.security.krb5.conf", "/etc/krb5.conf");
        String tableName = "test";
        HS2Tools tools = new HS2Tools();
        Connection connection = tools.getConnection();
        Statement statement = connection.createStatement();
        System.out.println("===显示表===");
        tools.showTables(statement);
        System.out.println("===建表详情===");
        tools.createTable(statement, tableName);
        tools.descTable(statement, tableName);
        System.out.println("===查询表===");
        tools.queryData(statement, tableName);
        System.out.println("===删除表===");
        tools.dropTable(statement, tableName);
        System.out.println("===显示表===");
        tools.showTables(statement);

        connection.close();
    }
}
