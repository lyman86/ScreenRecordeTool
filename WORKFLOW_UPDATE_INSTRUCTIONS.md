# GitHub Actions 工作流更新说明

## 背景
由于GitHub的安全限制，通过API更新工作流文件需要特殊的`workflow`权限。因此，需要手动更新`.github/workflows/build.yml`文件。

## 需要更新的文件
`.github/workflows/build.yml`

## 更新内容

### 1. 依赖安装步骤 (第46-58行)
将原来的：
```yaml
    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip setuptools wheel
        # Try CI requirements first
        pip install -r requirements-ci.txt || echo "CI requirements failed"
        # Ensure PyInstaller is available
        pip install PyInstaller || echo "PyInstaller failed"
```

替换为：
```yaml
    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip setuptools wheel
        # Install CI requirements
        pip install -r requirements-ci.txt
        # Verify critical dependencies
        python -c "import PyQt6; print('PyQt6 OK')"
        python -c "import cv2; print('OpenCV OK')"
        python -c "import numpy; print('NumPy OK')"
        python -c "import PIL; print('Pillow OK')"
        python -c "import mss; print('MSS OK')"
        python -c "import psutil; print('PSUtil OK')"
        python -c "import PyInstaller; print('PyInstaller OK')"
```

### 2. 添加诊断步骤 (第60行后插入)
在"Create resources directory"步骤后添加：
```yaml
    - name: Run CI diagnostics
      run: |
        if [ -f "diagnose_ci.py" ]; then
          python diagnose_ci.py
        else
          echo "Diagnostic script not found, skipping"
        fi
      continue-on-error: true
```

### 3. 测试步骤 (第73-79行)
将原来的：
```yaml
    - name: Run tests (if test files exist)
      run: |
        if [ -f "test_installation.py" ]; then
          python test_installation.py
        fi
      shell: bash
      continue-on-error: true
```

替换为：
```yaml
    - name: Run tests (if test files exist)
      run: |
        if [ -f "test_ci_build.py" ]; then
          python test_ci_build.py
        elif [ -f "test_installation.py" ]; then
          python test_installation.py
        else
          echo "No test files found, skipping tests"
        fi
      shell: bash
      env:
        QT_QPA_PLATFORM: offscreen
      continue-on-error: true
```

### 4. 构建步骤 (第90-95行)
将原来的：
```yaml
    - name: Build executable
      run: |
        python scripts/ci_build.py
      continue-on-error: true
```

替换为：
```yaml
    - name: Build executable
      run: |
        if [ -f "scripts/ci_build.py" ]; then
          echo "Using advanced CI build script"
          python scripts/ci_build.py
        elif [ -f "simple_build.py" ]; then
          echo "Using simple build script"
          python simple_build.py
        else
          echo "Using basic PyInstaller command"
          python -m PyInstaller --onefile --windowed --name ScreenRecorder main.py
        fi
      env:
        QT_QPA_PLATFORM: offscreen
        DISPLAY: ":99"
      continue-on-error: true
```

### 5. 构建输出检查 (第107行之前插入)
在上传artifact之前添加：
```yaml
    - name: List build output
      run: |
        echo "Checking build output..."
        ls -la dist/ || echo "No dist directory found"
        if [ -d "dist" ]; then
          find dist -type f -name "*" | head -20
        fi
      shell: bash
```

### 6. Artifact上传 (第116-143行)
将原来的：
```yaml
    - name: Upload Windows artifact
      if: runner.os == 'Windows' && hashFiles('dist/**/*') != ''
      uses: actions/upload-artifact@v3
      with:
        name: ScreenRecorder-Windows-${{ matrix.python-version }}
        path: |
          dist/
          !dist/**/*.pyc
      continue-on-error: true

    - name: Upload macOS artifact
      if: runner.os == 'macOS' && hashFiles('dist/**/*') != ''
      uses: actions/upload-artifact@v3
      with:
        name: ScreenRecorder-macOS-${{ matrix.python-version }}
        path: |
          dist/
          !dist/**/*.pyc
      continue-on-error: true
```

替换为：
```yaml
    - name: Upload Windows artifact
      if: runner.os == 'Windows' && hashFiles('dist/**/*') != ''
      uses: actions/upload-artifact@v3
      with:
        name: ScreenRecorder-Windows-${{ matrix.python-version }}
        path: |
          dist/
          !dist/**/*.pyc
        retention-days: 30

    - name: Upload macOS artifact
      if: runner.os == 'macOS' && hashFiles('dist/**/*') != ''
      uses: actions/upload-artifact@v3
      with:
        name: ScreenRecorder-macOS-${{ matrix.python-version }}
        path: |
          dist/
          !dist/**/*.pyc
        retention-days: 30
```

## 手动更新步骤

1. **在GitHub网页上编辑文件**：
   - 访问 https://github.com/lyman86/ScreenRecordeTool
   - 导航到 `.github/workflows/build.yml`
   - 点击编辑按钮（铅笔图标）

2. **应用上述更改**：
   - 按照上面的说明逐一更新各个部分
   - 确保YAML格式正确（注意缩进）

3. **提交更改**：
   - 添加提交消息："更新GitHub Actions工作流 - 修复自动打包问题"
   - 选择"Commit directly to the master branch"
   - 点击"Commit changes"

## 验证更新

更新完成后，可以通过以下方式验证：

1. **触发构建**：
   - 推送任何代码更改
   - 或者在Actions页面手动触发workflow

2. **检查构建日志**：
   - 查看依赖验证步骤是否通过
   - 确认构建输出列表正常显示
   - 验证artifact是否正确上传

3. **测试构建产物**：
   - 下载生成的artifact
   - 在目标平台上测试可执行文件

## 预期改进

更新后的工作流应该具有：
- ✅ 更稳定的依赖安装
- ✅ 更好的错误诊断
- ✅ 正确的无头模式支持
- ✅ 详细的构建输出信息
- ✅ 改进的artifact管理

## 故障排除

如果更新后仍有问题：

1. **检查语法**：确保YAML格式正确
2. **查看日志**：检查Actions运行日志中的错误信息
3. **回滚**：如有必要，可以恢复到之前的版本
4. **联系支持**：如果问题持续，可以创建issue

## 注意事项

- 更新工作流文件后，下次推送代码时会自动使用新的配置
- 建议在更新后进行一次完整的测试构建
- 保留原始文件的备份，以防需要回滚
