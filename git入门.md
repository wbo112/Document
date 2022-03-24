### git本地仓库操作

##### 创建本地仓库

`git init`就会将当前目录变成一个git仓库，同时当前目录也会有个`.git`的目录。

> 默认用`master`作为本地分支的名字，可以通过`git branch -m <name>`命令修改当前分支的名字。
>
> 当前执行`git branch`是查看不到当前的`master`分支的，那是因为当前我们还没有执行`git commit`操作。



`git add a.txt`就可以将`a.txt`添加到暂存区。



`git commit -m [日志] `将暂存区的所有文件提交到本地库。

`git commit -m [日志] [file]  ` 将暂存区的指定文件提交到本地库。

执行`git status`也会看到当前的工作区是干净的，没有要提交的东西。

这时我们再执行`git branch`就可以看到当前的`master`分支了。



##### 分支切换

`git checkout xxx`可以切换分支。但是如果对应分支不存在的话，那就会报错。

`git checkout -b xxx`如果分支不存在，那就需要添加`-b`参数，创建分支并切换。 

`git branch xxx`创建分支，但不切换分支

`git branch` 、`git branch -v`查看所有分支 



##### 分支合并

比如将`dev`分支的修改合并到`master`分支。

`git checkout  master`切换到`master`分支

`git merge dev` 就可以将`dev`分支的内容合并到`master`分支



##### 冲突处理:

>如果在合并分支过程中提示有冲突那就需要做如下处理。
>
>+ 如果当前冲突的是是一个文本文件，比如文件名是`a.txt`。那打开文件，将冲突的内容修改掉。重新执行`git add a.txt `,`git commit -m "xxx"`重新提交就可以了。
>
>+ 如果当前冲突的是二进制文件,比如文件名是`a.so`,这就不能通过手工的方式将它合并了。那就可以执行下面的命令
>
>  `git checkout a.so  --ours`或者`git checkout a.so --theirs`选择保留一个分支的，舍弃另一个分支的。
>
>  `--ours` 表示检出当前分支，即合并后保存当前分支的改动而丢弃另外一个分支的改动。
>
>  `--theirs` 表示检出另外一个分支，即保存另外一个分支的改动丢弃当前分支的改动。
>
>  重新执行`git add a.so `,`git commit -m "xxx"`重新提交就可以了。





##### 删除文件

**从本地库中删除`a.txt`**

`git rm a.txt` 这会将这个删除操作提交到暂存区，也会本地删除`a.txt`这个文件。如果想保留本地的文件不被删除，那就需要添加`--cache`参数。对应的命令就是`git rm a.txt --cached`

`git commit -m "delete a.txt" 将这次删除提交到本地库`

**从暂存区中删除a.txt**

`git restore --staged a.txt` 



##### 还原文件

如果文件`a.txt`已经修改了，但是之前我们已经添加到暂存区或者已经提交到了本地库，现在想还原`a.txt`

**从暂存区中还原:**

`git restore a.txt`

**从本地库中还原:**

​	`git reset  a.txt`执行完这个操作a.txt并没有被还原。主要是为了避免本地工作区中的修改丢失。

​	`git restore a.txt` 继续执行完这个操作后就可以将本地库中最新的`a.txt`还原到工作区

> ​	要还原本地库中之前提交的版本:
>
> ​	`git log a.txt`查看文件提交记录，获取commit id
>
> ​	`git reset [commit id] a.txt` 还原指定版本
>
> ​	`git restore a.txt`

`git checkout a.txt`也可以还原a.txt。如果暂存区有，就还原暂存区的，否则就还原本地库的。**这个命令还是比较危险的，会将当前工作区中的文件直接覆盖掉。**



##### 查看历史提交日志

`git log`查看历史提交日志,如果有版本回退，回退版本之后的历史提交日志这个命令是看不到的。

它有好多种格式化输出形式`git log --graph --pretty=oneline`、`git log --oneline`等等。

`git reflog`也可以查看历史提交日志。与`git log `不同的是它会显示所有历史提交记录，包括回退版本之后的。

常用的形式`git reflog  show`



##### 版本回退

`git reset --hard [局部索引值] ` 回退到指定版本

`git reset --soft  [局部索引值]  `

`git reset --mixed  [局部索引值]`

> soft 仅仅在本地库中移动head指针
>
> mixed 在本地库移动head指针，同时重置暂存区
>
> hard 在本地库移动head指针，同时重置暂存区、重置工作区



使用^符号只能后退

`git reset --hard HEAD^`     一个^表示后退一步，n个表示后退n步

使用~符号:只能后退

`git reset --hard HEAD~n`    表示后退n步



##### 将当前修改保存到堆栈区

`git stash` 将当前的修改保存在堆栈区

`git stash save [日志] ` 将当前的修改保存在堆栈区

`git stash list`查看当前所有的堆栈区保存列表

`git stash pop`还原最近的stash。同时从堆栈区中删除。

`git stash pop [数字]`还原指定stash。同时从堆栈区中删除。

`git stash drop [数字] `删除堆栈区中指定stash。

`git stash show` 显示最近堆栈区和工作区的差异.`git stash show -p`可以显示更详细的内容。

`git stash show [数字]`、`git stash show -p [数字]`比较堆栈区中指定的stash和工作区

`git stash clear`清空





##### 比较文件差异

`git diff [file]`  将工作区的文件和暂存区的比较
`git diff [本地库中的历史版本] [file]`  将工作区中的文件和本地库历史记录比较

> 不带文件名比较所有差异文件



### 远程仓库操作，如`github`

##### 本地仓库与远程仓库关联

`git remote add [远程仓库别名] [远程仓库地址]`将本地仓库与远程仓库关联

如`git remote add origin git@gitee.com:wbo112/gitdemo.git`



##### 本地仓库与远程仓库断开关联

`git remote rm [远程仓库别名] ` 将本地仓库与远程仓库断开关联



##### 将本地库内容推送到远程仓库

`git push  [远程仓库别名] [本地仓库分支名]`将本地仓库对应分支推送到远程仓库，如果远程仓库没有与本地对应分支名，就会在远程仓库创建一个对应分支。

如我本地有个`dev`分支。执行` git push  origin dev`就会将本地`dev`分支的内容推送到远程仓库`dev`分支，如果远程仓库没有`dev`分支，就会在远程仓库创建个`dev`分支。



`git push  [远程仓库别名] [本地仓库分支名]:[远程仓库分支名]`

我本地有个`dev`分支。执行` git push  origin dev:odev`就会将本地`dev`分支的内容推送到远程仓库`odev`，如果远程仓库没有`odev`分支，就会在远程仓库创建个`odev`分支。

> 如果本地分支与远程仓库分支名字相同，可以添加`-u`参数将其设置为默认推送、拉取分支，以后就可以直接使用`git push`进行推送，使用`git pull`之类的拉取。
>
> 如使用`git push -u origin dev`将本地`dev`分支推送给远程仓库`dev`分支，同时将远程`dev`设置为默认推送分支。以后推送就可以直接使用`git push`、`git pull`了。



从远程仓库拉取代码

`git pull [远程仓库别名] [远程仓库分支名]:[本地分支名]`将远程仓库 的 对应分支拉取过来，与本地的分支合并。

`git fetch `