



```shell


git add <file>     # 添加到本地暂存库
git restore <file>    #取消文件修改，还原本次之前暂存库

git rm --cache <file>    #从本地暂存区删除文件
git commit -m "xxx"   <file>   #将本地暂存区文件提交到本地库。<file>可以省略，将提交本地暂存区所有文件

git log #显示本地提交日志
git log --pretty=oneline   #显示本地提交日志
git log --oneline      #显示本地提交日志

git reflog    #显示本地提交日志


#基于索引值操作[推荐]
git reset --hard [局部索引值] 
git reset --hard a6ace91
#还有
#git reset --soft  [局部索引值]   
#git reset --mixed  [局部索引值]
# soft 仅仅在本地库中移动head指针
# mixed 在本地库移动head指针，同时重置暂存区
# hard 在本地库移动head指针，同时重置暂存区、重置工作区

#使用^符号只能后退
git reset --hard [局部索引值]    #版本回退
git reset --hard HEAD^    #  注:一个^表示后退一步，n个表示后退n步
#使用~符号:只能后退
git reset --hard HEAD~n  #   注:表示后退n步


git status  #查看工作区，暂存区的状态


###################比较文件差异############################

git diff [file]  #将工作区的文件和暂存区的比较
git diff [本地库中的历史版本] [file]  #将工作区中的文件和本地库历史记录比较
#不带文件名比较多个文件



#####################分支操作############################
git branch [分支名]   #创建分支
git branch -v        #查看分支
git checkout [分支名] #切换分支

#合并分支
#1.切换到接受修改的分支(被合并，增加新内容的分支)上
  git checkout [被合并分支名]
#2.执行合并操作
  git merge [有新内容的分支]


#解决冲突

#文本内容冲突
#1.删除冲突文件中的特殊符号。 <<<<<<HEAD ======= >>>>>>> master 之类
#2. git add [文件名]  重新添加到暂存区
#3. git commit -m "日志"  #注意此处不能带具体文件名

#二进制文件冲突
#1. git checkout [file] --ours{--theirs}
--ours 表示检出当前分支，即合并后保存当前分支的改动而丢弃另外一个分支的改动。
--theirs 表示检出另外一个分支，即保存另外一个分支的改动丢弃当前分支的改动。
#2. git add [文件名]
#3. git commit -m "日志"  #注意此处不能带具体文件名
```







git本地代码合并到github。

+ 在本地目录中执行`git init`,初始化本地目录。
+ 在github网站新建仓库，拷贝仓库URL。如`git@github.com:wbo112/githubdemo.git`
+ 在本地目录中执行`git remote add origin git@github.com:wbo112/githubdemo.git`,将本地仓库与远程仓库(github)关联。
+ 执行`git push origin master`,将本地仓库文件推送到远程仓库(github)。





`git remote -v `  查看当前所有远程地址别名

`git remote add [别名] [远程地址]`  创建远程库地址别名

`git push [别名] [分支名]` 推送到远程地址

`git clone [远程地址]` 将远程库克隆到本地
