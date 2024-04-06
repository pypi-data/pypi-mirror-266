# findyourip

因为运营商不提供静态IP地址，`findyourip` 可以帮助你通过爬取IP池来获取当前的公网IP地址。

## 功能

- **单次IP获取**：执行命令后获取一次当前的公网IP地址。
- **多次IP获取**：通过指定次数 `n`，可以多次获取公网IP地址，有助于从IP池中获取不同的IP地址。

## 使用方法

- 获取一次IP地址：
  
  ```
  ip
  ```

- 获取N次IP地址：

  ```
  ip n
  ```

  其中，`n` 是您希望获取IP地址的次数。

## 安装

目前，`findyourip` 可以通过源代码安装。将来可能会提供 `pip` 安装方式。

1. 克隆仓库到本地：

   ```
   git clone https://github.com/yourusername/findyourip.git
   ```

2. 切换到仓库目录：

   ```
   cd findyourip
   ```

3. 安装依赖（如果有）：

   ```
   pipx install .
   ```

## 贡献

欢迎任何形式的贡献，无论是新功能的建议、bug 修复还是文档改进。请通过 GitHub 的 Pull Request 或 Issue 进行贡献。

## 许可证

`findyourip` 根据 MIT 许可证发布。关于许可证的更多信息，请查看 `LICENSE` 文件。

---