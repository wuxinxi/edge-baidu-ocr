<template>
  <div class="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-indigo-500/30">
    <!-- 顶部导航栏 -->
    <header class="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50 px-6 py-3 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="h-9 w-9 rounded-xl bg-gradient-to-tr from-indigo-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-indigo-500/20 text-white">
          <ScanText class="w-5 h-5" />
        </div>
        <div>
          <div class="flex items-center gap-2.5">
            <h1 class="text-base font-bold tracking-tight text-white">edge-ocr</h1>
            <span class="text-[11px] font-medium px-2 py-0.5 rounded-full bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">
              baidu/Unlimited-OCR · 端侧长文档一次前向解析工作台
            </span>
            <span class="hidden sm:inline-flex text-[11px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/25">
              R-SWA Window = 128
            </span>
          </div>
          <p class="text-xs text-slate-400 mt-0.5">
            3B MoE (激活 500M) · 16× DeepEncoder 视觉压缩 · 恒定解码 KV 缓存 · 边看图边流式框选抄书
          </p>
        </div>
      </div>

      <!-- 硬件与统一内存监控 -->
      <div class="flex items-center gap-3">
        <div v-if="systemInfo" class="hidden xl:flex items-center space-x-3 text-xs bg-slate-800/70 px-3.5 py-1.5 rounded-lg border border-slate-700/60">
          <div class="flex items-center gap-1.5 text-slate-200 font-medium">
            <Cpu class="w-3.5 h-3.5 text-emerald-400" />
            <span>{{ systemInfo.chip }}</span>
          </div>
          <span class="text-slate-600">|</span>
          <div class="text-slate-300">
            统一内存:
            <span class="text-cyan-400 font-semibold">{{ systemInfo.memory_available_gb }}GB</span> 可用 /
            {{ systemInfo.memory_total_gb }}GB
          </div>
          <span class="text-slate-600">|</span>
          <div class="flex items-center gap-1">
            <span class="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span class="text-slate-300">Apple Vision ANE + MLX 就绪</span>
          </div>
        </div>

        <button
          @click="showDownloadModal = true"
          class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-medium flex items-center gap-1.5 transition"
        >
          <Download class="w-3.5 h-3.5 text-indigo-400" />
          <span>模型管理</span>
        </button>
      </div>
    </header>

    <!-- 顶部控制栏：3 套典型测试样本切换 + 上传 PDF/扫描图 + Base/Gundam 模式 + 流式解析 -->
    <section class="border-b border-slate-800/80 bg-slate-900/40 px-6 py-3">
      <div class="max-w-[1640px] mx-auto flex flex-col gap-2.5">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <!-- 左侧：用户上传 PDF / 扫描图片 -->
          <div class="flex flex-wrap items-center gap-3">
            <label
              class="cursor-pointer px-4 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 border border-indigo-500/50 text-xs font-semibold text-white flex items-center gap-1.5 transition shadow-md shadow-indigo-600/20"
            >
              <Upload class="w-3.5 h-3.5" />
              <span>{{ isUploading ? '正在上传...' : '上传 PDF / 扫描图片' }}</span>
              <input type="file" accept=".pdf,.png,.jpg,.jpeg,.webp" class="hidden" @change="onFileUpload" />
            </label>

            <div
              v-if="currentDoc"
              class="px-3 py-1.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs text-slate-300 flex items-center gap-2"
            >
              <FileText class="w-3.5 h-3.5 text-indigo-400 shrink-0" />
              <span class="font-medium text-slate-100">{{ currentDoc.filename }}</span>
              <span class="text-[11px] text-slate-500 font-mono">({{ currentDoc.page_count }} 页)</span>
            </div>
            <span v-else class="text-xs text-slate-400">
              支持上传多页 <code class="text-slate-300">.pdf</code> 或单张扫描图 <code class="text-slate-300">.png / .jpg / .webp</code>
            </span>
          </div>

          <!-- 右侧：模型选择 + 分辨率模式 (Base vs Gundam) + 流式抄书启动按钮 -->
          <div class="flex flex-wrap items-center gap-2.5">
            <!-- 模型选择 -->
            <div class="flex items-center gap-1.5 bg-slate-900 border border-slate-800 rounded-xl px-2.5 py-1.5 text-xs">
              <Layers class="w-3.5 h-3.5 text-indigo-400 shrink-0" />
              <select
                v-model="selectedModelKey"
                class="bg-transparent text-slate-100 font-medium focus:outline-none cursor-pointer pr-1"
              >
                <option v-for="m in models" :key="m.key" :value="m.key" class="bg-slate-900 text-slate-100">
                  {{ m.name }} {{ m.downloaded ? '✅' : '(本地未下·用 ANE 视觉引擎)' }}
                </option>
              </select>
            </div>

            <!-- 分辨率模式切换：Base vs Gundam -->
            <div class="flex items-center bg-slate-900 p-0.5 rounded-xl border border-slate-800 text-xs">
              <button
                @click="switchImageMode('base')"
                :class="[
                  'px-2.5 py-1 rounded-lg font-medium transition flex items-center gap-1',
                  imageMode === 'base'
                    ? 'bg-indigo-600 text-white shadow'
                    : 'text-slate-400 hover:text-slate-200'
                ]"
                title="多页 PDF 连跑标准模式：整页压为 1024×1024 (256 视觉 Tokens)，速度最快但 6pt 极小脚注略模糊"
              >
                <span>Base 多页模式 (1024)</span>
              </button>
              <button
                @click="switchImageMode('gundam')"
                :class="[
                  'px-2.5 py-1 rounded-lg font-medium transition flex items-center gap-1',
                  imageMode === 'gundam'
                    ? 'bg-amber-600 text-white shadow'
                    : 'text-slate-400 hover:text-slate-200'
                ]"
                title="单页高密模式：1024 全局底图 + 4 张 640×640 动态高清切片，100% 还原 6pt 极小字号脚注与密集表格"
              >
                <span>Gundam 动态切片 (1024+640×4)</span>
              </button>
            </div>

            <!-- 流式 One-shot 解析按钮 -->
            <button
              @click="runStreamingOcr"
              :disabled="!currentDoc || isParsing"
              class="px-4 py-1.5 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 disabled:opacity-50 text-white text-xs font-semibold flex items-center gap-1.5 shadow-lg shadow-indigo-600/25 transition"
            >
              <Loader2 v-if="isParsing" class="w-4 h-4 animate-spin" />
              <Sparkles v-else class="w-4 h-4" />
              <span>{{ isParsing ? '正在流式抄书解析...' : '流式 One-shot 解析' }}</span>
            </button>
          </div>
        </div>

        <!-- R-SWA 人眼抄书滑动窗口实时可视化条 -->
        <div class="bg-slate-950/90 border border-slate-800/90 rounded-xl px-4 py-2.5 flex flex-col lg:flex-row lg:items-center justify-between gap-3">
          <div class="flex items-center gap-2.5 shrink-0">
            <span class="px-2 py-0.5 rounded bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-[11px] font-mono font-semibold flex items-center gap-1">
              <Activity class="w-3 h-3" />
              R-SWA 抄书工作记忆
            </span>
            <span class="text-xs text-slate-300">
              前缀锁死
              <strong class="text-indigo-400 font-mono">{{ liveTelemetry.visual_prefix_tokens }}</strong> 视觉 Tokens ·
              文字窗口仅留最近
              <strong class="text-emerald-400 font-mono">{{ liveTelemetry.active_window_tokens }} / 128</strong> Tokens ·
              已滑出软遗忘
              <strong class="text-slate-400 font-mono">{{ liveTelemetry.forgotten_tokens }}</strong> Tokens (零显存累加)
            </span>
          </div>

          <!-- 实时笔尖滑动窗口文字预览 -->
          <div class="flex items-center gap-2 min-w-0 flex-1 lg:max-w-xl justify-end">
            <span class="text-[11px] text-slate-500 shrink-0 font-mono">笔尖窗口 D_128(t):</span>
            <div class="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-[11px] font-mono text-emerald-300 truncate flex-1">
              {{ liveTelemetry.window_preview || '等待开始流式抄书...' }}
            </div>
            <span
              v-if="pageTurnBanner"
              class="px-2 py-0.5 rounded bg-amber-500/20 border border-amber-500/40 text-amber-300 text-[11px] font-mono animate-bounce shrink-0"
            >
              {{ pageTurnBanner }}
            </span>
          </div>
        </div>
      </div>
    </section>

    <!-- 顶部 4 卡片性能看板 -->
    <section class="px-6 pt-3.5">
      <div class="max-w-[1640px] mx-auto grid grid-cols-2 lg:grid-cols-4 gap-3">
        <div class="bg-slate-900/70 border border-slate-800/90 rounded-xl p-3 flex items-center justify-between">
          <div>
            <p class="text-[11px] text-slate-400">单次前向连跑规模 &amp; 模式</p>
            <p class="text-base font-bold text-white mt-0.5">
              {{ currentDoc?.page_count || 0 }} 页 · {{ imageMode === 'gundam' ? 'Gundam 高清切片' : 'Base 1024全局' }}
              <span class="text-xs font-normal text-indigo-400 ml-1">
                (前缀 {{ liveTelemetry.visual_prefix_tokens }} Tokens)
              </span>
            </p>
          </div>
          <div class="h-8 w-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <BookOpen class="w-4 h-4" />
          </div>
        </div>

        <div class="bg-slate-900/70 border border-slate-800/90 rounded-xl p-3 flex items-center justify-between">
          <div>
            <p class="text-[11px] text-slate-400">R-SWA 恒定解码 KV 缓存</p>
            <p class="text-base font-bold text-emerald-400 mt-0.5">
              {{ liveTelemetry.rswa_kv_cache_tokens }} Tokens
              <span class="text-xs font-normal text-slate-400 ml-1">
                (传统 MHA 需 {{ liveTelemetry.mha_kv_cache_tokens }} · 省 {{ liveTelemetry.kv_saving_percent }}%)
              </span>
            </p>
          </div>
          <div class="h-8 w-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <Zap class="w-4 h-4" />
          </div>
        </div>

        <div class="bg-slate-900/70 border border-slate-800/90 rounded-xl p-3 flex items-center justify-between">
          <div>
            <p class="text-[11px] text-slate-400">M1 Pro 实测流式吞吐 &amp; 进度</p>
            <p class="text-base font-bold text-cyan-400 mt-0.5">
              {{ liveTelemetry.tokens_per_second }} <span class="text-xs font-normal">tokens/s</span>
              <span class="text-xs font-normal text-slate-400 ml-1">
                (已吐出 {{ liveTelemetry.cumulative_tokens }} tokens · {{ liveTelemetry.elapsed_seconds }}s)
              </span>
            </p>
          </div>
          <div class="h-8 w-8 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
            <Gauge class="w-4 h-4" />
          </div>
        </div>

        <div class="bg-slate-900/70 border border-slate-800/90 rounded-xl p-3 flex items-center justify-between">
          <div>
            <p class="text-[11px] text-slate-400">防复读约束 &amp; 当前页区块</p>
            <p class="text-base font-bold text-amber-300 mt-0.5">
              {{ currentPageBoxes.length }} 个 &lt;|det|&gt; 框
              <span class="text-xs font-normal text-slate-400 ml-1">
                (no_repeat_ngram = 35)
              </span>
            </p>
          </div>
          <div class="h-8 w-8 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
            <BoxSelect class="w-4 h-4" />
          </div>
        </div>
      </div>
    </section>

    <!-- 主工作区：左栏 PDF/图片画布 + 实时生长的 <|det|> 框 + Gundam 网格 | 右栏 富文本预览 / 区块 / 原生流 / 缓存曲线 -->
    <main class="flex-1 p-6 max-w-[1640px] w-full mx-auto grid grid-cols-1 lg:grid-cols-12 gap-5 min-h-0">
      <!-- 左栏 (7 列) -->
      <div class="lg:col-span-7 bg-slate-900/60 border border-slate-800 rounded-2xl flex flex-col overflow-hidden">
        <!-- 左栏顶部工具条 -->
        <div class="px-4 py-2.5 border-b border-slate-800 flex flex-wrap items-center justify-between gap-2 bg-slate-900/80">
          <div class="flex items-center gap-2">
            <Eye class="w-4 h-4 text-indigo-400" />
            <span class="text-xs font-semibold text-white">
              原文档画布与 &lt;|det|&gt; 坐标定位
            </span>
            <span v-if="currentDoc" class="text-xs text-slate-400">
              (第 {{ activePageIndex + 1 }} / {{ currentDoc.page_count }} 页)
            </span>
          </div>

          <div class="flex flex-wrap items-center gap-2 text-[11px]">
            <button
              @click="showBoxes = !showBoxes"
              :class="[
                'px-2.5 py-1 rounded-md border font-medium transition flex items-center gap-1',
                showBoxes
                  ? 'bg-indigo-500/20 border-indigo-500/40 text-indigo-300'
                  : 'bg-slate-800 border-slate-700 text-slate-400'
              ]"
            >
              <BoxSelect class="w-3.5 h-3.5" />
              <span>{{ showBoxes ? '检测框 ON' : '检测框 OFF' }}</span>
            </button>

            <button
              @click="showGundamGrid = !showGundamGrid"
              :class="[
                'px-2.5 py-1 rounded-md border font-medium transition flex items-center gap-1',
                showGundamGrid
                  ? 'bg-amber-500/20 border-amber-500/40 text-amber-300'
                  : 'bg-slate-800 border-slate-700 text-slate-400'
              ]"
            >
              <Grid class="w-3.5 h-3.5" />
              <span>{{ imageMode === 'gundam' ? 'Gundam 4×640 切片网格 ON' : '查看视觉切片网格' }}</span>
            </button>

            <span
              v-for="cat in categoryLegend"
              :key="cat.key"
              class="hidden xl:inline-flex px-2 py-0.5 rounded border items-center gap-1"
              :class="cat.badgeClass"
            >
              <span class="w-2 h-2 rounded-full" :class="cat.dotClass"></span>
              {{ cat.label }}
            </span>
          </div>
        </div>

        <!-- 左栏主体 -->
        <div v-if="currentDoc" class="flex-1 flex min-h-[580px] overflow-hidden">
          <!-- 页码缩略图导航 -->
          <div class="w-28 border-r border-slate-800 bg-slate-950/60 p-2.5 space-y-2.5 overflow-y-auto shrink-0">
            <button
              v-for="(p, idx) in currentDoc.pages"
              :key="p.page_num"
              @click="activePageIndex = idx"
              :class="[
                'w-full rounded-xl p-1.5 border text-left transition relative',
                activePageIndex === idx
                  ? 'border-indigo-500 bg-indigo-500/15 shadow-md shadow-indigo-500/10'
                  : 'border-slate-800 hover:border-slate-700 bg-slate-900/50'
              ]"
            >
              <div class="aspect-[1/1.38] w-full bg-white rounded-lg overflow-hidden mb-1 relative">
                <img :src="p.image_url" :alt="`Page ${p.page_num}`" class="w-full h-full object-contain" />
                <div
                  v-if="isParsing && activePageIndex === idx"
                  class="absolute inset-0 bg-indigo-500/15 border-2 border-indigo-400 animate-pulse flex items-end justify-center p-1"
                >
                  <span class="px-1.5 py-0.5 rounded bg-indigo-600 text-[9px] text-white font-bold">正在抄写</span>
                </div>
              </div>
              <div class="flex items-center justify-between px-0.5 text-[11px]">
                <span :class="activePageIndex === idx ? 'text-indigo-300 font-semibold' : 'text-slate-400'">
                  第 {{ p.page_num }} 页
                </span>
                <span class="text-[10px] text-emerald-400 font-mono">
                  {{ (streamedPages[idx]?.boxes || []).length }}框
                </span>
              </div>
            </button>
          </div>

          <!-- 页面主画布 -->
          <div class="flex-1 bg-slate-950/80 p-5 overflow-auto flex flex-col items-center">
            <!-- Base vs Gundam 模式针对 6pt 极小字号的对比提示条 -->
            <div
              v-if="activeSampleId === 'dense_scan_png'"
              class="w-full max-w-[590px] mb-3 px-3.5 py-2 rounded-xl border text-xs flex items-center justify-between gap-2"
              :class="
                imageMode === 'gundam'
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-200'
                  : 'bg-amber-500/10 border-amber-500/30 text-amber-200'
              "
            >
              <div class="flex items-center gap-2">
                <Sparkles class="w-4 h-4 shrink-0" />
                <span v-if="imageMode === 'gundam'">
                  已开启 <strong>Gundam 模式 (1024全局 + 4×640高清切片)</strong>：底部 6pt 极小序列号 <code>#SN-884920-B01</code> 与公差 <code>+/-0.0035mm</code> 100% 精准还原！
                </span>
                <span v-else>
                  当前为 <strong>Base 模式 (1024全局压缩)</strong>：底部 6pt 极小字号出现轻微模糊（<code>#SN-8B492O-801</code>）。点右上角切换至 <strong>Gundam 动态切片</strong> 即可对比修复效果！
                </span>
              </div>
            </div>

            <div
              v-if="activePageMeta"
              class="relative bg-white rounded-lg shadow-2xl border border-slate-700 select-none max-w-full"
              style="width: 590px;"
            >
              <img
                :src="activePageMeta.image_url"
                :alt="`Page ${activePageMeta.page_num}`"
                class="w-full h-auto block rounded-lg"
              />

              <!-- DeepEncoder Gundam 640×640 动态切片网格叠加层 -->
              <template v-if="showGundamGrid && currentPageGundamTiles.length">
                <div
                  v-for="tile in currentPageGundamTiles"
                  :key="tile.tile_id"
                  :style="getBoxStyle(tile.bbox_1000)"
                  class="absolute border-2 border-dashed border-amber-400/80 bg-amber-400/5 pointer-events-none z-30 rounded-md"
                >
                  <span class="absolute bottom-1 right-1 px-1.5 py-0.5 rounded bg-amber-600/90 text-white text-[9px] font-mono shadow">
                    {{ tile.label }} ({{ tile.tokens }} tokens)
                  </span>
                </div>
              </template>

              <!-- <|det|> 0-1000 归一化坐标框叠加层 -->
              <template v-if="showBoxes && currentPageBoxes.length">
                <div
                  v-for="(box, bIdx) in currentPageBoxes"
                  :key="box.id"
                  @mouseenter="hoveredBoxId = box.id"
                  @mouseleave="hoveredBoxId = null"
                  @click="scrollToBlock(box.id)"
                  :style="getBoxStyle(box.bbox_1000)"
                  :class="[
                    'absolute border-2 rounded transition-all cursor-pointer',
                    getCategoryStyle(box.category).boxClass,
                    activeStreamingBoxId === box.id
                      ? 'ring-4 ring-emerald-400/90 bg-emerald-400/20 z-30 scale-[1.01]'
                      : hoveredBoxId === box.id
                        ? 'ring-2 ring-offset-1 ring-indigo-400 z-20 scale-[1.005]'
                        : 'z-10'
                  ]"
                >
                  <span
                    class="absolute -top-5 left-0 px-1.5 py-0.2 rounded text-[10px] font-mono font-semibold text-white shadow whitespace-nowrap flex items-center gap-1"
                    :class="activeStreamingBoxId === box.id ? 'bg-emerald-600' : getCategoryStyle(box.category).tagClass"
                  >
                    <span v-if="activeStreamingBoxId === box.id">✍️ 正在抄写</span>
                    <span>#{{ bIdx + 1 }} {{ box.category }} [{{ box.bbox_1000.join(',') }}]</span>
                  </span>
                </div>
              </template>
            </div>
          </div>
        </div>

        <!-- 未上传文档时的拖拽/点击上传空状态 -->
        <div
          v-else
          @dragover.prevent="isDragOver = true"
          @dragleave.prevent="isDragOver = false"
          @drop.prevent="onDropFile"
          class="flex-1 min-h-[580px] p-8 flex items-center justify-center bg-slate-950/60"
        >
          <label
            :class="[
              'w-full max-w-xl rounded-2xl border-2 border-dashed p-10 flex flex-col items-center justify-center text-center cursor-pointer transition-all',
              isDragOver
                ? 'border-indigo-400 bg-indigo-500/10 scale-[1.01]'
                : 'border-slate-800 hover:border-indigo-500/60 bg-slate-900/40 hover:bg-slate-900/70'
            ]"
          >
            <div class="w-14 h-14 rounded-2xl bg-indigo-500/15 border border-indigo-500/30 flex items-center justify-center text-indigo-400 mb-4 shadow-lg shadow-indigo-500/10">
              <Upload class="w-7 h-7" />
            </div>
            <h3 class="text-base font-bold text-white mb-1.5">
              {{ isUploading ? '正在上传并渲染页面...' : '点击选择或拖拽上传 PDF 文档 / 扫描图片' }}
            </h3>
            <p class="text-xs text-slate-400 max-w-md leading-relaxed">
              支持多页 <code class="text-indigo-300">.pdf</code> 文档及单张图片 <code class="text-indigo-300">.png / .jpg / .jpeg / .webp</code>。上传后将调用本地 M1 Pro GPU (<code class="text-emerald-300">mlx-vlm</code>) 实时流式输出 <code class="text-amber-300">&lt;|det|&gt;</code> 坐标框与 Markdown。
            </p>
            <span class="mt-5 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/20 transition">
              选择本地文件上传
            </span>
            <input type="file" accept=".pdf,.png,.jpg,.jpeg,.webp" class="hidden" @change="onFileUpload" />
          </label>
        </div>
      </div>

      <!-- 右栏 (5 列)：富文本排版预览 / 结构化区块 / 原生 <|det|> 流 / R-SWA 缓存曲线 -->
      <div class="lg:col-span-5 bg-slate-900/60 border border-slate-800 rounded-2xl flex flex-col overflow-hidden">
        <!-- 右栏顶部 Tab 切换 -->
        <div class="px-4 py-2.5 border-b border-slate-800 bg-slate-900/80 flex items-center justify-between gap-2">
          <div class="flex items-center space-x-1 text-xs overflow-x-auto">
            <button
              v-for="tab in resultTabs"
              :key="tab.id"
              @click="activeResultTab = tab.id"
              :class="[
                'px-2.5 py-1.5 rounded-lg font-medium transition flex items-center gap-1.5 whitespace-nowrap',
                activeResultTab === tab.id
                  ? 'bg-indigo-600 text-white shadow'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              ]"
            >
              <component :is="tab.icon" class="w-3.5 h-3.5" />
              <span>{{ tab.label }}</span>
            </button>
          </div>

          <button
            v-if="fullCleanMarkdown"
            @click="copyMarkdown"
            class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-[11px] flex items-center gap-1 transition shrink-0"
          >
            <Check v-if="copied" class="w-3.5 h-3.5 text-emerald-400" />
            <Copy v-else class="w-3.5 h-3.5 text-slate-400" />
            <span>{{ copied ? '已复制' : '复制 MD' }}</span>
          </button>
        </div>

        <!-- 右栏内容区 -->
        <div class="flex-1 p-4 overflow-y-auto space-y-3 max-h-[640px]">
          <div
            v-if="!currentDoc"
            class="h-full min-h-[420px] flex flex-col items-center justify-center text-center text-slate-500 px-6"
          >
            <ScanText class="w-10 h-10 text-slate-700 mb-3" />
            <p class="text-sm font-medium text-slate-400">等待上传 PDF 或图片</p>
            <p class="text-xs text-slate-500 mt-1">上传后将在此处实时渲染 HTML 表格、数学公式块、干净 Markdown 与原生 &lt;|det|&gt; 坐标流</p>
          </div>

          <!-- Tab 1: 富文本排版预览 (真正渲染表格、标题、公式卡片与小字差异提示) -->
          <template v-else-if="activeResultTab === 'rendered'">
            <div class="flex items-center justify-between text-xs text-slate-400 pb-1">
              <span>第 {{ activePageIndex + 1 }} 页富文本还原对照（点击卡片可在左图定位）</span>
              <span class="font-mono text-emerald-400">{{ liveTelemetry.engine }}</span>
            </div>

            <div
              v-for="(box, bIdx) in currentPageBoxes"
              :key="box.id"
              :id="`block-${box.id}`"
              @mouseenter="hoveredBoxId = box.id"
              @mouseleave="hoveredBoxId = null"
              :class="[
                'p-3.5 rounded-xl border transition',
                activeStreamingBoxId === box.id
                  ? 'bg-emerald-950/30 border-emerald-500 shadow-lg'
                  : hoveredBoxId === box.id
                    ? 'bg-slate-800/90 border-indigo-500'
                    : 'bg-slate-950/70 border-slate-800/90'
              ]"
            >
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-2">
                  <span
                    class="px-2 py-0.5 rounded text-[10px] font-mono font-semibold text-white"
                    :class="getCategoryStyle(box.category).tagClass"
                  >
                    #{{ bIdx + 1 }} {{ box.category.toUpperCase() }}
                  </span>
                  <span class="text-[11px] font-mono text-slate-500">
                    [{{ box.bbox_1000.join(', ') }}]
                  </span>
                </div>
                <span v-if="activeStreamingBoxId === box.id" class="text-[11px] text-emerald-400 font-mono animate-pulse">
                  ● 正在解码输出...
                </span>
              </div>

              <!-- 针对表格区块真正渲染为 HTML 表格 -->
              <div v-if="box.category === 'table'" class="overflow-x-auto">
                <table class="w-full text-left border-collapse text-xs border border-slate-700 rounded-lg overflow-hidden">
                  <thead>
                    <tr class="bg-indigo-950/60 text-indigo-200 border-b border-slate-700">
                      <th
                        v-for="(cell, cIdx) in parseMarkdownTable(box.content).headers"
                        :key="cIdx"
                        class="py-1.5 px-2.5 border-r border-slate-700/80 font-semibold"
                      >
                        {{ cell }}
                      </th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-800">
                    <tr
                      v-for="(row, rIdx) in parseMarkdownTable(box.content).rows"
                      :key="rIdx"
                      class="hover:bg-slate-900/60"
                    >
                      <td
                        v-for="(cell, cIdx) in row"
                        :key="cIdx"
                        class="py-1.5 px-2.5 border-r border-slate-800 text-slate-200 font-mono text-[11px]"
                      >
                        {{ cell }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- 针对公式区块渲染为数学公式展示卡 -->
              <div
                v-else-if="box.category === 'formula'"
                class="bg-amber-950/20 border border-amber-500/30 rounded-lg p-3 font-mono text-xs text-amber-200 overflow-x-auto"
              >
                <div class="text-[10px] text-amber-400/80 mb-1">LaTeX / Mathematical Expression</div>
                <div class="whitespace-pre-wrap">{{ stripFormulaDelimiters(box.content) }}</div>
              </div>

              <!-- 针对标题区块渲染为醒目标题 -->
              <div v-else-if="box.category === 'title'" class="text-sm font-bold text-white tracking-tight">
                {{ box.content.replace(/^#+\s*/, '') }}
              </div>

              <!-- 针对代码区块 -->
              <pre
                v-else-if="box.category === 'code'"
                class="bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-xs font-mono text-cyan-300 overflow-x-auto"
              >{{ stripCodeDelimiters(box.content) }}</pre>

              <!-- 正文与列表 -->
              <p v-else class="text-xs text-slate-200 leading-relaxed whitespace-pre-wrap">
                {{ box.content }}
              </p>

              <!-- Base 模式下 6pt 极小字号差异警告 -->
              <div
                v-if="box.mode_note"
                class="mt-2 px-2.5 py-1.5 rounded-lg bg-amber-500/15 border border-amber-500/40 text-[11px] text-amber-300 flex items-center justify-between gap-2"
              >
                <span>⚠️ {{ box.mode_note }}</span>
                <button
                  @click="switchImageMode('gundam')"
                  class="px-2 py-0.5 rounded bg-amber-500 hover:bg-amber-400 text-slate-950 font-semibold shrink-0 transition"
                >
                  切到 Gundam 修复
                </button>
              </div>
            </div>
          </template>

          <!-- Tab 2: 剥离 <|det|> 后的全文干净 Markdown 源码 -->
          <template v-else-if="activeResultTab === 'markdown'">
            <div class="bg-slate-950 border border-slate-800 rounded-xl p-4">
              <div class="flex items-center justify-between text-[11px] text-slate-400 mb-2 pb-2 border-b border-slate-800">
                <span>已自动执行官方 remove_det() 正则清洗（剥离坐标框与 &lt;page&gt; 分隔符）</span>
                <span class="text-emerald-400 font-mono">可直接入库 RAG / 知识库</span>
              </div>
              <pre class="text-xs text-slate-200 whitespace-pre-wrap font-mono leading-relaxed">{{ fullCleanMarkdown }}</pre>
            </div>
          </template>

          <!-- Tab 3: 模型原生 <|det|> + <page> 实时吐字流 -->
          <template v-else-if="activeResultTab === 'raw'">
            <div class="bg-slate-950 border border-slate-800 rounded-xl p-4">
              <div class="flex items-center justify-between text-[11px] text-slate-400 mb-2 pb-2 border-b border-slate-800">
                <span>Unlimited-OCR 原生输出格式：&lt;|det|&gt;类别 [x1, y1, x2, y2]&lt;|/det|&gt; + &lt;page&gt;</span>
                <span class="text-amber-400 font-mono">0–1000 归一化坐标</span>
              </div>
              <pre class="text-xs text-amber-200/90 whitespace-pre-wrap font-mono leading-relaxed">{{ fullRawOutput }}</pre>
            </div>
          </template>

          <!-- Tab 4: R-SWA 恒定缓存 vs 传统 MHA 线性膨胀可视化对比 -->
          <template v-else-if="activeResultTab === 'rswa'">
            <div class="space-y-4">
              <div class="bg-slate-950/90 border border-slate-800 rounded-xl p-4 space-y-2">
                <h4 class="text-xs font-semibold text-white flex items-center gap-1.5">
                  <Zap class="w-4 h-4 text-emerald-400" />
                  <span>R-SWA (参考滑动窗口注意力) 核心机制验证</span>
                </h4>
                <p class="text-xs text-slate-300 leading-relaxed">
                  传统 MHA 的解码 KV 缓存随输出长度线性膨胀（<code class="text-rose-300">L_m + T</code>），输出到 6000 tokens 时速度下跌 35%。
                  Unlimited-OCR 锁定全局图片前缀 <code class="text-indigo-300">L_m</code>，文字解码只留最近
                  <code class="text-emerald-300">128 tokens</code>，缓存恒定为 <code class="text-emerald-300">L_m + 128</code>。
                </p>
              </div>

              <!-- 可视化进度条对比 -->
              <div class="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-3">
                <div class="text-xs font-semibold text-slate-200">逐页解码 KV 缓存体积对比 (越短越省显存)</div>
                <div v-for="pt in rswaCurve" :key="pt.page" class="space-y-1.5 text-xs">
                  <div class="flex justify-between text-[11px] text-slate-400 font-mono">
                    <span>第 {{ pt.page }} 页结束 (累计吐字 {{ pt.cumulative_tokens }} tokens)</span>
                    <span class="text-emerald-400">节省 {{ pt.kv_saving_percent }}% 缓存</span>
                  </div>
                  <div class="space-y-1">
                    <div class="flex items-center gap-2">
                      <span class="w-24 text-[10px] text-emerald-400 font-mono shrink-0">R-SWA (恒定)</span>
                      <div class="flex-1 bg-slate-900 rounded-full h-3 overflow-hidden">
                        <div
                          class="bg-emerald-500 h-full rounded-full transition-all duration-300"
                          :style="{ width: `${Math.min(100, (pt.rswa_kv_cache_tokens / maxMhaTokens) * 100)}%` }"
                        ></div>
                      </div>
                      <span class="w-16 text-right text-[10px] font-mono text-emerald-300">{{ pt.rswa_kv_cache_tokens }}</span>
                    </div>
                    <div class="flex items-center gap-2">
                      <span class="w-24 text-[10px] text-rose-400 font-mono shrink-0">传统 MHA</span>
                      <div class="flex-1 bg-slate-900 rounded-full h-3 overflow-hidden">
                        <div
                          class="bg-rose-500 h-full rounded-full transition-all duration-300"
                          :style="{ width: `${Math.min(100, (pt.mha_kv_cache_tokens / maxMhaTokens) * 100)}%` }"
                        ></div>
                      </div>
                      <span class="w-16 text-right text-[10px] font-mono text-rose-300">{{ pt.mha_kv_cache_tokens }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </main>

    <!-- 模型下载管理弹窗 -->
    <div
      v-if="showDownloadModal"
      class="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4"
      @click.self="showDownloadModal = false"
    >
      <div class="bg-slate-900 border border-slate-700 rounded-2xl max-w-2xl w-full p-6 space-y-4 shadow-2xl">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <div class="flex items-center gap-2">
            <Download class="w-5 h-5 text-indigo-400" />
            <h3 class="text-base font-bold text-white">Unlimited-OCR 模型矩阵与本地下载指南 (Mac M1 Pro 16GB)</h3>
          </div>
          <button @click="showDownloadModal = false" class="text-slate-400 hover:text-white text-sm">✕</button>
        </div>

        <div class="space-y-2.5 max-h-[340px] overflow-y-auto pr-1">
          <div
            v-for="m in models"
            :key="m.key"
            class="p-3.5 rounded-xl bg-slate-950 border border-slate-800 flex items-start justify-between gap-3"
          >
            <div class="space-y-1">
              <div class="flex items-center gap-2">
                <span class="text-xs font-bold text-white">{{ m.name }}</span>
                <span class="text-[10px] px-2 py-0.5 rounded bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">
                  {{ m.download_size }}
                </span>
                <span
                  v-if="m.recommended_m1"
                  class="text-[10px] px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-300 border border-emerald-500/30"
                >
                  M1 16GB 推荐
                </span>
              </div>
              <p class="text-xs text-slate-400">{{ m.desc }}</p>
              <code class="block text-[11px] text-cyan-300 bg-slate-900 px-2.5 py-1 rounded border border-slate-800 mt-1">
                ./download.sh --model {{ m.key }}
              </code>
            </div>
            <span
              class="shrink-0 text-xs font-medium px-2.5 py-1 rounded-lg border"
              :class="
                m.downloaded
                  ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-300'
                  : 'bg-slate-800 border-slate-700 text-slate-400'
              "
            >
              {{ m.downloaded ? `✅ 已就绪 (${m.downloaded_size_mb}MB)` : '未下载' }}
            </span>
          </div>
        </div>

        <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-3 text-xs text-slate-300 space-y-1">
          <p class="font-semibold text-indigo-300">💡 终端一键下载命令（支持断点续传与国内镜像加速）：</p>
          <code class="block text-emerald-300 font-mono">./download.sh --recommended</code>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import {
  ScanText,
  Cpu,
  Download,
  Upload,
  FileText,
  Layers,
  Sparkles,
  Loader2,
  BookOpen,
  Zap,
  Gauge,
  BoxSelect,
  Eye,
  Copy,
  Check,
  Code2,
  AlignLeft,
  Activity,
  Grid,
  LayoutTemplate
} from 'lucide-vue-next'

const systemInfo = ref<any>(null)
const models = ref<any[]>([])
const presetSamples = ref<any[]>([])
const activeSampleId = ref<string>('benchmark_3pages')
const selectedModelKey = ref('unlimited-ocr-mlx-4bit')
const imageMode = ref<'base' | 'gundam'>('base')

const currentDoc = ref<any>(null)
const activePageIndex = ref(0)
const isUploading = ref(false)
const isParsing = ref(false)

// 流式累积页面数据
const streamedPages = ref<Array<{ page: number; boxes: any[]; gundam_tiles: any[] }>>([])
const activeStreamingBoxId = ref<string | null>(null)
const pageTurnBanner = ref<string>('')
const fullRawOutput = ref<string>('')
const fullCleanMarkdown = ref<string>('')
const rswaCurve = ref<any[]>([])

const liveTelemetry = reactive({
  engine: 'apple-vision-ane',
  visual_prefix_tokens: 768,
  active_window_tokens: 0,
  forgotten_tokens: 0,
  cumulative_tokens: 0,
  rswa_kv_cache_tokens: 768,
  mha_kv_cache_tokens: 768,
  kv_saving_percent: 0,
  tokens_per_second: 0,
  elapsed_seconds: 0,
  window_preview: ''
})

const showBoxes = ref(true)
const showGundamGrid = ref(false)
const hoveredBoxId = ref<string | null>(null)
const activeResultTab = ref<'rendered' | 'markdown' | 'raw' | 'rswa'>('rendered')
const showDownloadModal = ref(false)
const copied = ref(false)

const resultTabs = [
  { id: 'rendered', label: '富文本排版预览', icon: LayoutTemplate },
  { id: 'markdown', label: '干净 Markdown', icon: AlignLeft },
  { id: 'raw', label: '原生 <|det|> 流', icon: Code2 },
  { id: 'rswa', label: 'R-SWA 缓存曲线', icon: Activity }
] as const

const categoryLegend = [
  { key: 'title', label: '标题 Title', badgeClass: 'bg-indigo-500/10 border-indigo-500/30 text-indigo-300', dotClass: 'bg-indigo-400' },
  { key: 'text', label: '正文 Text', badgeClass: 'bg-sky-500/10 border-sky-500/30 text-sky-300', dotClass: 'bg-sky-400' },
  { key: 'table', label: '表格 Table', badgeClass: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300', dotClass: 'bg-emerald-400' },
  { key: 'formula', label: '公式 Formula', badgeClass: 'bg-amber-500/10 border-amber-500/30 text-amber-300', dotClass: 'bg-amber-400' },
  { key: 'code', label: '代码 Code', badgeClass: 'bg-purple-500/10 border-purple-500/30 text-purple-300', dotClass: 'bg-purple-400' }
]

const activePageMeta = computed(() => {
  if (!currentDoc.value || !currentDoc.value.pages?.length) return null
  return currentDoc.value.pages[activePageIndex.value] || currentDoc.value.pages[0]
})

const currentPageBoxes = computed(() => {
  return streamedPages.value[activePageIndex.value]?.boxes || []
})

const currentPageGundamTiles = computed(() => {
  return streamedPages.value[activePageIndex.value]?.gundam_tiles || []
})

const maxMhaTokens = computed(() => {
  if (!rswaCurve.value.length) return 2000
  return Math.max(...rswaCurve.value.map((p: any) => p.mha_kv_cache_tokens), 1000)
})

function getBoxStyle(bbox1000: number[]) {
  const [x1, y1, x2, y2] = bbox1000
  return {
    left: `${(x1 / 10).toFixed(2)}%`,
    top: `${(y1 / 10).toFixed(2)}%`,
    width: `${Math.max(1, (x2 - x1) / 10).toFixed(2)}%`,
    height: `${Math.max(1, (y2 - y1) / 10).toFixed(2)}%`
  }
}

function getCategoryStyle(category: string) {
  switch (category) {
    case 'title':
      return {
        boxClass: 'border-indigo-500 bg-indigo-500/10 hover:bg-indigo-500/20',
        tagClass: 'bg-indigo-600'
      }
    case 'table':
      return {
        boxClass: 'border-emerald-500 bg-emerald-500/10 hover:bg-emerald-500/20',
        tagClass: 'bg-emerald-600'
      }
    case 'formula':
      return {
        boxClass: 'border-amber-500 bg-amber-500/10 hover:bg-amber-500/20',
        tagClass: 'bg-amber-600'
      }
    case 'code':
      return {
        boxClass: 'border-purple-500 bg-purple-500/10 hover:bg-purple-500/20',
        tagClass: 'bg-purple-600'
      }
    default:
      return {
        boxClass: 'border-sky-500 bg-sky-500/10 hover:bg-sky-500/20',
        tagClass: 'bg-sky-600'
      }
  }
}

function parseMarkdownTable(md: string) {
  const lines = md
    .trim()
    .split('\n')
    .map((l) => l.trim())
    .filter((l) => l.startsWith('|'))
  if (!lines.length) return { headers: [], rows: [] }
  const parseRow = (line: string) =>
    line
      .replace(/^\|/, '')
      .replace(/\|$/, '')
      .split('|')
      .map((c) => c.trim())
  const headers = parseRow(lines[0])
  const rows = lines.slice(2).map(parseRow)
  return { headers, rows }
}

function stripFormulaDelimiters(txt: string) {
  return txt.replace(/^\$\$\n?/, '').replace(/\n?\$\$$/, '').trim()
}

function stripCodeDelimiters(txt: string) {
  return txt.replace(/^```[a-zA-Z]*\n?/, '').replace(/\n?```$/, '').trim()
}

function scrollToBlock(boxId: string) {
  activeResultTab.value = 'rendered'
  setTimeout(() => {
    const el = document.getElementById(`block-${boxId}`)
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }, 40)
}

async function switchImageMode(mode: 'base' | 'gundam') {
  imageMode.value = mode
  showGundamGrid.value = mode === 'gundam'
  if (currentDoc.value && !isParsing.value) {
    await runStreamingOcr()
  }
}

async function fetchInitialData() {
  try {
    const [sysRes, modRes, smpRes] = await Promise.all([
      fetch('/api/system/info'),
      fetch('/api/models'),
      fetch('/api/samples')
    ])
    if (sysRes.ok) systemInfo.value = await sysRes.json()
    if (modRes.ok) {
      const data = await modRes.json()
      models.value = data.models || []
    }
    if (smpRes.ok) {
      const data = await smpRes.json()
      presetSamples.value = data.samples || []
    }
  } catch (e) {
    console.error('Failed to load initial data:', e)
  }
}

const isDragOver = ref(false)

async function uploadRawFile(file: File) {
  activeSampleId.value = ''
  isUploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    const res = await fetch('/api/pdf/upload', {
      method: 'POST',
      body: formData
    })
    if (!res.ok) throw new Error('文件上传失败')
    currentDoc.value = await res.json()
    activePageIndex.value = 0
    await runStreamingOcr()
  } catch (e) {
    console.error(e)
  } finally {
    isUploading.value = false
  }
}

async function onFileUpload(ev: Event) {
  const input = ev.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  await uploadRawFile(file)
  input.value = ''
}

async function onDropFile(ev: DragEvent) {
  isDragOver.value = false
  const file = ev.dataTransfer?.files?.[0]
  if (!file) return
  await uploadRawFile(file)
}

async function runStreamingOcr() {
  if (!currentDoc.value || isParsing.value) return
  isParsing.value = true
  activeStreamingBoxId.value = null
  pageTurnBanner.value = ''
  fullRawOutput.value = ''
  fullCleanMarkdown.value = ''
  rswaCurve.value = []

  streamedPages.value = Array.from({ length: currentDoc.value.page_count }, (_, i) => ({
    page: i + 1,
    boxes: [],
    gundam_tiles: []
  }))

  try {
    const res = await fetch('/api/ocr/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        doc_id: currentDoc.value.doc_id,
        model_key: selectedModelKey.value,
        image_mode: imageMode.value,
        ngram_size: 35,
        sliding_window: 128
      })
    })
    if (!res.ok || !res.body) throw new Error('流式解析请求失败')

    const reader = res.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''

    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const parts = buffer.split('\n\n')
      buffer = parts.pop() || ''

      for (const chunk of parts) {
        const line = chunk.trim()
        if (!line.startsWith('data:')) continue
        const payload = JSON.parse(line.slice(5).trim())

        if (payload.type === 'init') {
          liveTelemetry.engine = payload.engine
          liveTelemetry.visual_prefix_tokens = payload.visual_prefix_tokens
          liveTelemetry.rswa_kv_cache_tokens = payload.visual_prefix_tokens
          liveTelemetry.mha_kv_cache_tokens = payload.visual_prefix_tokens
          liveTelemetry.active_window_tokens = 0
          liveTelemetry.forgotten_tokens = 0
          liveTelemetry.cumulative_tokens = 0
        } else if (payload.type === 'page_start') {
          const pIdx = payload.page - 1
          activePageIndex.value = pIdx
          if (streamedPages.value[pIdx]) {
            streamedPages.value[pIdx].gundam_tiles = payload.gundam_tiles || []
          }
        } else if (payload.type === 'box_step') {
          const pIdx = payload.page - 1
          if (streamedPages.value[pIdx]) {
            streamedPages.value[pIdx].boxes.push(payload.box)
          }
          activeStreamingBoxId.value = payload.box.id
          fullRawOutput.value += (fullRawOutput.value ? '\n' : '') + payload.det_line
          fullCleanMarkdown.value += (fullCleanMarkdown.value ? '\n\n' : '') + payload.box.content

          liveTelemetry.cumulative_tokens = payload.cumulative_tokens
          liveTelemetry.active_window_tokens = payload.active_window_tokens
          liveTelemetry.forgotten_tokens = payload.forgotten_tokens
          liveTelemetry.rswa_kv_cache_tokens = payload.rswa_kv_cache_tokens
          liveTelemetry.mha_kv_cache_tokens = payload.mha_kv_cache_tokens
          liveTelemetry.kv_saving_percent = payload.kv_saving_percent
          liveTelemetry.window_preview = payload.window_preview
          liveTelemetry.elapsed_seconds = payload.elapsed_seconds
          liveTelemetry.tokens_per_second = payload.tokens_per_second
        } else if (payload.type === 'page_turn') {
          fullRawOutput.value += '\n<page>\n'
          pageTurnBanner.value = `吐出 ${payload.token} → 自动翻至第 ${payload.to_page} 页`
          setTimeout(() => {
            pageTurnBanner.value = ''
          }, 1200)
        } else if (payload.type === 'complete') {
          activeStreamingBoxId.value = null
          fullRawOutput.value = payload.full_raw_output
          fullCleanMarkdown.value = payload.full_clean_markdown
          rswaCurve.value = payload.rswa_curve || []
        }
      }
    }
  } catch (e) {
    console.error(e)
  } finally {
    isParsing.value = false
    activeStreamingBoxId.value = null
  }
}

async function copyMarkdown() {
  if (!fullCleanMarkdown.value) return
  await navigator.clipboard.writeText(fullCleanMarkdown.value)
  copied.value = true
  setTimeout(() => {
    copied.value = false
  }, 1800)
}

onMounted(async () => {
  await fetchInitialData()
})
</script>
