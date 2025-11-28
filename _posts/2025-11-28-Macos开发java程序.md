---
layout: post
title: macOS 开发 Java 程序
date: 2025-11-28 10:00 +0800
categories: [编程, Java]
tags: [Java, macOS]
---

macOS 上进行 Java 开发的快速入门与实践，涵盖 JDK 安装、环境变量配置、常用构建工具、IDE 选择、项目创建与调试，以及常见问题排查。

## 安装 JDK
推荐使用 Adoptium 的 Temurin 或 Homebrew 的 OpenJDK。

```bash
# 使用 Homebrew 安装（优先）
brew update
brew install openjdk@21

# 链接至系统路径（如提示未自动链接）
sudo ln -sfn /opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk \
  /Library/Java/JavaVirtualMachines/openjdk-21.jdk

# 验证
/usr/libexec/java_home -V
java -version
javac -version
```

也可从 Adoptium 官方下载安装包（Temurin）：
```bash
# 访问 https://adoptium.net/ 下载安装 17/21 LTS
# 安装后验证版本
java -version
```

## 配置环境变量
使用系统工具自动解析 `JAVA_HOME`。

```bash
# 临时设置（当前终端）
export JAVA_HOME=$(/usr/libexec/java_home -v 21)
export PATH="$JAVA_HOME/bin:$PATH"

# 永久设置（zsh）
echo 'export JAVA_HOME=$(/usr/libexec/java_home -v 21)' >> ~/.zshrc
echo 'export PATH="$JAVA_HOME/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

多版本管理可选：
```bash
# jenv 管理多个 JDK 版本
brew install jenv
mkdir -p ~/.jenv/versions
export PATH="$HOME/.jenv/bin:$PATH"
eval "$(jenv init -)"

# 添加 JDK 并切换版本
jenv add $(/usr/libexec/java_home -v 21)
jenv add $(/usr/libexec/java_home -v 17)
jenv global 21
```

## 构建工具
常用 Maven 与 Gradle。

```bash
# 安装 Maven
brew install maven
mvn -v

# 安装 Gradle
brew install gradle
gradle -v
```

## IDE 与编辑器
```bash
# IntelliJ IDEA（推荐社区版）
brew install --cask intellij-idea-ce

# VS Code + Java 扩展
brew install --cask visual-studio-code
# 在 VS Code 扩展商店安装 "Extension Pack for Java"
```

## 第一个 Java 程序
```bash
# 创建并编译
cat > Hello.java <<'EOF'
public class Hello {
  public static void main(String[] args) {
    System.out.println("Hello, Java on macOS!");
  }
}
EOF

javac Hello.java
java Hello
```

## 使用 Maven 创建项目
```bash
# 交互式创建骨架项目
mvn archetype:generate \
  -DgroupId=com.example \
  -DartifactId=demo \
  -DarchetypeArtifactId=maven-archetype-quickstart \
  -DinteractiveMode=false

cd demo
mvn clean package
```

## 使用 Gradle 创建项目
```bash
gradle init --type java-application
cd .
./gradlew build
./gradlew run
```

## 调试与运行
```bash
# 启动带调试端口（示例 5005）
java -agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:5005 -jar app.jar

# IDE 连接远程调试：配置 Host 与 5005 端口
```

## 常见问题排查
- 找不到 `java`：确认 `JAVA_HOME` 与 `PATH` 设置，或使用 `/usr/libexec/java_home -V` 检查版本。
- 权限与安全提示：首次运行 IDE 或 JDK 组件可能触发 Gatekeeper，前往 系统设置 → 隐私与安全 允许运行。
- 证书与 HTTPS 访问异常：更新根证书或使用 `keytool` 导入企业证书。
- 多版本冲突：优先使用 `jenv` 管理，避免手动覆盖 `JAVA_HOME`。

## 优化建议
- 选择 LTS JDK（17/21）用于生产与长期维护。
- 使用 IDE 的 Maven/Gradle 集成简化构建与依赖管理。
- 为大型项目启用 Gradle Daemon 与本地缓存以加速构建。
