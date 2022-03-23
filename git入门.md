git入门

1.创建本地仓库

1.首先在本地新建目录，比如`mkdir gitdemo`，执行`cd gitdemo`进入这个目录。

2.当前目录中是空的。执行`git init`,就会将当前目录变成一个git仓库，同时当前目录也会有个`.git`的目录。

同时从执行`git init`返回的日志中也可以看到会用master作为本地分支的名字，可以通过`git branch -m <name>`命令修改当前分支的名字。

当前执行`git branch`是查看不到当前的`master`分支的，那是因为当前我们还没有执行`git commit`操作。

3.我们在当前目录新建个文件，执行`touch a.txt`新建个`a.txt`的文件。这时执行`git status`查看当前仓库状态，会提示新创建的`a.txt`状态是`untracked`的，也就是没有被`git`管理。

执行`git add a.txt`就可以将`a.txt`添加到暂存区。



从图上也可以看出，`a.txt`添加到暂存区后，我们还可以执行通过`git rm --cached a.txt`将文件从暂存区中移除。也能看到这里会告诉我们这些变更的文件需要被`commit`。

下面我们就可以执行`git commit -m "xxx"`将暂存区的文件提交到本地库。



再执行`git status`也会看到当前的工作区是干净的，没有要提交的东西。

这时我们再执行`git branch`就可以看到当前的`master`分支了。



分支切换

`git checkout xxx`可以切换分支。但是如果对应分支不存在的话，那就会报错。

`git checkout -b xxx`如果分支不存在，那就需要添加`-b`参数，创建分支并切换。  



分支合并

比如将`dev`分支的修改合并到`master`分支。

`git checkout  master`切换到`master`分支

`git merge dev` 就可以将`dev`分支的内容合并到`master`分支



冲突处理:

>如果在合并分支过程中提示有冲突那就需要做如下处理。
>
>+ 如果当前冲突的是是一个文本文件，比如文件名是`a.txt`。那打开文件，将冲突的内容修改掉。重新执行`git add a.txt `,`git commit -m "xxx"`重新提交就可以了。
>
>+ 如果当前冲突的是二进制文件,比如文件名是`a.so`,这就不能通过手工的方式将它合并了。那就可以执行下面的命令
>
>  `git checkout a.so  --ours`或者`git checkout a.so --theirs`选择保留一个分支的，舍弃另一个分支的。
>
>  `--ours` 表示检出当前分支，即合并后保存当前分支的改动而丢弃另外一个分支的改动。
>  `--theirs` 表示检出另外一个分支，即保存另外一个分支的改动丢弃当前分支的改动。
>
>  重新执行`git add a.so `,`git commit -m "xxx"`重新提交就可以了。





删除文件

如果文件`a.txt`已经添加到了暂存区或者提交到了本地库中,现在需要删除这个文件。



从本地库中删除的`a.txt`

`git rm a.txt` 这会将这个删除操作提交到暂存区，也会本地删除`a.txt`这个文件。如果想保留本地的文件不被删除，那就需要添加`--cache`参数。对应的命令就是`git rm a.txt --cached`

`git commit -m "delete a.txt" 将这次删除提交到本地库`

从暂存区中删除

`git restore --staged a.txt` 

> 也可以执行`git rm`，相当于个撤销动作，不需要后面的`git commit`命令了。



还原文件

如果文件`a.txt`已经修改了，但是之前我们已经添加到暂存区或者已经提交到了本地库，现在想还原`a.txt`

从暂存区中还原:`git restore a.txt`

从本地库中还原:

`git reset  a.txt`执行完这个操作a.txt并没有被还原。主要是为了避免本地工作区中的修改丢失。

`git restore a.txt` 继续执行完这个操作后就可以将本地库中最新的`a.txt`还原到工作区

> 要还原本地库中之前提交的版本:
>
> `git log a.txt`查看文件提交记录，获取commit id
>
> `git reset [commit id] a.txt` 还原指定版本
>
> `git restore a.txt`



`git checkout a.txt`也可以还原a.txt。如果暂存区有，就还原暂存区的，否则就还原本地库的。