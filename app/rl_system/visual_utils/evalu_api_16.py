import sys
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import re

# 获取用户选择的路口 ID
if len(sys.argv) > 1:
    selected_intersections = [int(id) for id in sys.argv[1:] if 0 <= int(id) <= 15]
else:
    selected_intersections = list(range(16))  # 默认显示所有路口


# ----------------- 日志解析函数 -----------------
def parse_log(filename):
    """
    解析日志文件，提取训练指标与各路口数据
    返回：
      data = {
          'q_loss': [q_loss,...],
          'rewards': [rewards,...],
          'delay': [delay,...],
          'throughput': [throughput,...],
          'intersections': {0: {'reward': [...], 'queue': [...]},
                            1: {'reward': [...], 'queue': [...]},
                             ...
                            15: {'reward': [...], 'queue': [...]}
                           }
      }
    """
    with open(filename, 'r') as f:
        lines = f.readlines()

    data = {
        'q_loss': [],
        'rewards': [],
        'delay': [],
        'throughput': [],
        'intersections': {i: {'reward': [], 'queue': []} for i in range(16)}
    }

    # 按顺序解析数据，当遇到 step: 行和 intersection: 行
    for line in lines:
        line = line.strip()
        if line.startswith('step:'):
            # 提取训练指标（假设每行中均包含 q_loss, rewards, delay, throughput）
            q_loss = float(re.search(r'q_loss:([-\d.]+)', line).group(1))
            rewards_val = float(re.search(r'rewards:([-\d.]+)', line).group(1))
            delay = float(re.search(r'delay:([-\d.]+)', line).group(1))
            throughput = float(re.search(r'throughput:(\d+)', line).group(1))

            data['q_loss'].append(q_loss)
            data['rewards'].append(rewards_val)
            data['delay'].append(delay)
            data['throughput'].append(throughput)

        elif line.startswith('intersection:'):
            # 提取 intersection 行数据（假设行中依次包含 intersection id, mean_episode_reward, mean_queue）
            idx = int(re.search(r'intersection:(\d+)', line).group(1))
            reward = float(re.search(r'mean_episode_reward:([-\d.]+)', line).group(1))
            queue = float(re.search(r'mean_queue:([-\d.]+)', line).group(1))
            data['intersections'][idx]['reward'].append(reward)
            data['intersections'][idx]['queue'].append(queue)
    return data

# ----------------- 数据加载 -----------------
log_file = './data/output_data/tsc/sumo_colight/sumohz4x4/test/logger/model_eva.log'
data = parse_log(log_file)

# 总的训练数据条数（以 step 行为单位）
num_frames = len(data['q_loss'])
# 我们每5轮更新一次显示，故有效帧数为
num_steps = (num_frames + 4) // 5  # 向上取整

# ----------------- Figure 1: 训练指标图 -----------------
fig_train, ax_train = plt.subplots()
line_q, = ax_train.plot([], [], marker='o', label='q_loss')
line_r, = ax_train.plot([], [], marker='s', label='rewards')
line_d, = ax_train.plot([], [], marker='^', label='delay')
ax_train.set_title('Training Metrics')
ax_train.set_xlabel('episode')
ax_train.set_ylabel('metrics')

# 创建双 y 轴用于 throughput
ax_tp = ax_train.twinx()
line_tp, = ax_tp.plot([], [], marker='x', color='green', label='throughput')
ax_tp.set_ylabel('throughput')

# 设置图例
lines = [line_q, line_r, line_d, line_tp]
labels = [line.get_label() for line in lines]
ax_train.legend(lines, labels, loc='upper left')
ax_train.grid(True)

def update_training(frame):
    idx = frame * 5
    if idx >= num_frames:
        idx = num_frames - 1
    x = list(range(idx + 1))
    line_q.set_data(x, data['q_loss'][:idx+1])
    line_r.set_data(x, data['rewards'][:idx+1])
    line_d.set_data(x, data['delay'][:idx+1])
    line_tp.set_data(x, data['throughput'][:idx+1])
    ax_train.relim()
    ax_train.autoscale_view()
    ax_tp.relim()
    ax_tp.autoscale_view()
    return line_q, line_r, line_d, line_tp

anim_train = FuncAnimation(fig_train, update_training, frames=num_steps, interval=800, blit=False)


# ----------------- Figure 3: 各个路口图 -----------------
intersection_anims = {}
intersection_figs = {}

def create_intersection_fig(inter_id):
    fig, ax = plt.subplots()
    line_r = ax.plot([], [], marker='o', linestyle='-', label='reward')[0]
    line_q = ax.plot([], [], marker='s', linestyle='--', label='queue')[0]
    ax.set_title(f'Intersection {inter_id}')
    ax.set_xlabel('step')
    ax.set_ylabel('value')
    ax.legend(fontsize='small')
    ax.grid(True)
    return fig, ax, line_r, line_q

# 只为用户选择的路口创建图形和动画
for i in selected_intersections:
    fig_i, ax_i, line_r_i, line_q_i = create_intersection_fig(i)
    intersection_figs[i] = (fig_i, ax_i, line_r_i, line_q_i)

    def update_intersection(frame, inter_id=i, ax=ax_i, line_r=line_r_i, line_q=line_q_i):
        idx = frame * 5
        if idx >= num_frames:
            idx = num_frames - 1
        x = list(range(idx + 1))
        rewards_i = data['intersections'][inter_id]['reward'][:idx+1]
        queues_i = data['intersections'][inter_id]['queue'][:idx+1]
        line_r.set_data(x[:len(rewards_i)], rewards_i)
        line_q.set_data(x[:len(queues_i)], queues_i)
        ax.relim()
        ax.autoscale_view()
        return line_r, line_q

    anim = FuncAnimation(intersection_figs[i][0],
                         update_intersection,
                         frames=num_steps,
                         interval=800,
                         blit=False)
    intersection_anims[i] = anim

# ----------------- 展示所有 Figure -----------------
plt.show()