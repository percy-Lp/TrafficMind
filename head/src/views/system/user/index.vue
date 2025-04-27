<template>
  <div class="dashboard-container">
    <div class="chart-wrapper">
      <div class="content">
        <!-- 卡片式用户管理 -->
        <div class="card card-float">
          <div class="card-header">
            <div class="card-title">用户管理</div>
            <div class="card-badge">✨ 系统用户</div>
          </div>

          <div class="card-child">
            <!-- 搜索栏 -->
            <div class="search-container">
              <el-form :model="queryParams" :inline="true">
                <el-form-item label="用户昵称">
                  <el-input
                    @keyup.enter="handleQuery"
                    v-model="queryParams.keyword"
                    style="width: 200px"
                    placeholder="请输入用户昵称"
                    clearable
                  />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" icon="Search" @click="handleQuery"
                    >搜索</el-button
                  >
                </el-form-item>
              </el-form>
            </div>

            <!-- 表格展示 -->
            <div class="table-container">
              <el-table
                border
                :data="userList"
                v-loading="loading"
                class="custom-table"
              >
                <!-- id -->
                <el-table-column
                  prop="id"
                  label="用户ID"
                  align="center"
                  width="100"
                  class="el-table-column--id"
                ></el-table-column>
                <!-- 用户头像 -->
                <el-table-column
                  prop="avatar"
                  label="头像"
                  align="center"
                  width="100"
                  class="el-table-column--avatar"
                >
                  <template #default="scope">
                    <div class="avatar-container">
                      <img :src="scope.row.avatar" class="user-avatar" />
                    </div>
                  </template>
                </el-table-column>
                <!-- 昵称 -->
                <el-table-column
                  prop="username"
                  label="用户昵称"
                  align="center"
                  width="200"
                  class="el-table-column--username"
                ></el-table-column>
                <!-- 用户角色 -->
                <el-table-column prop="grade" label="用户角色" align="center">
                </el-table-column>
                <!-- 邮箱 -->
                <el-table-column prop="email" label="邮箱" align="center">
                </el-table-column>
                <!-- 操作 -->
                <el-table-column
                  label="操作"
                  align="center"
                  width="100"
                  class="el-table-column--action"
                >
                  <template #default="scope">
                    <el-button
                      type="primary"
                      class="edit-button"
                      @click="openModel(scope.row)"
                    >
                      编辑
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>

            <!-- 分页 -->
            <div class="pagination-container">
              <pagination
                v-if="count > 0"
                :total="count"
                v-model:page="queryParams.current"
                v-model:limit="queryParams.size"
                @pagination="getList"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加或修改对话框 -->
    <el-dialog
      title="修改用户"
      v-model="update"
      width="500px"
      append-to-body
      class="custom-dialog"
    >
      <el-form
        ref="userFormRef"
        label-width="100px"
        :model="userForm"
        :rules="rules"
        class="user-form"
      >
        <el-form-item label="昵称" prop="username">
          <el-input
            placeholder="请输入昵称"
            v-model="userForm.username"
            style="width: 250px"
          />
        </el-form-item>
        <el-form-item label="角色" prop="grade">
          <el-input
            placeholder="请输入角色"
            v-model="userForm.grade"
            style="width: 250px"
          />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input
            placeholder="请输入email"
            v-model="userForm.email"
            style="width: 250px"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="submitForm">确 定</el-button>
          <el-button @click="update = false">取 消</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import {
  getUserList,
  getUserRoleList,
  updateUser,
  updateUserStatus,
} from "@/api/user";
import { User, UserForm, UserQuery, UserRole } from "@/api/user/types";
import { formatDate } from "@/utils/date";
import { messageConfirm, notifySuccess } from "@/utils/modal";
import { FormInstance, FormRules } from "element-plus";
import { onMounted, reactive, ref, toRefs } from "vue";

const userFormRef = ref<FormInstance>();
const rules = reactive<FormRules>({
  username: [{ required: true, message: "请输入昵称", trigger: "blur" }],
  roleIdList: [{ required: true, message: "角色不能为空", trigger: "click" }],
});
const data = reactive({
  count: 0,
  update: false,
  loading: false,
  queryParams: {
    current: 1,
    size: 10,
  } as UserQuery,
  typeList: [
    {
      value: 1,
      label: "邮箱",
    },
    {
      value: 2,
      label: "QQ",
    },
    {
      value: 3,
      label: "Gitee",
    },
    {
      value: 4,
      label: "Github",
    },
  ],
  userList: [] as User[],
  userForm: {} as UserForm,
  userRoleList: [] as UserRole[],
  roleIdList: [] as string[],
});
const {
  count,
  update,
  loading,
  queryParams,
  typeList,
  userList,
  userForm,
  userRoleList,
  roleIdList,
} = toRefs(data);
const openModel = (user: User) => {
  roleIdList.value = [];
  userForm.value.id = user.id;
  userForm.value.username = user.username;
  userForm.value.grade = user.grade;
  userForm.value.email = user.email;
  userFormRef.value?.clearValidate();
  update.value = true;
};


const submitForm = () => {
  // 表单验证
  userFormRef.value?.validate((valid) => {
    if (valid) {
      updateUser(userForm.value).then(({ data }) => {
        if (data.flag) {
          // 显示成功提示
          notifySuccess(data.msg);
          // 刷新用户列表
          getList();
        }
        // 关闭模态框
        update.value = false;
      });
    }
  });
};
const getList = () => {
  loading.value = true;
  getUserList(queryParams.value.current).then(({ data }) => {
    console.log(data);
    userList.value = data.data;
    loading.value = false;
  });
};
// 搜索方法
const handleQuery = () => {
  queryParams.value.current = 1;
};

onMounted(() => {
  getList();
});
</script>

<style scoped>
:root {
  --primary-color: #2563eb;
  --primary-dark: #1d4ed8;
  --primary-light: #dbeafe;
  --secondary-color: #0f172a;
  --accent-color: #3b82f6;
  --text-primary: #1e293b;
  --text-secondary: #475569;
  --bg-primary: #f8fafc;
  --bg-secondary: #f1f5f9;
  --bg-card: #ffffff;
  --border-color: #e2e8f0;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.05);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.05);
}

.dashboard-container {
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
  background-color: #f0f2f5;
  overflow: auto;
  min-height: 100vh;
  font-family: "PingFang SC", "Helvetica Neue", Helvetica, Arial, sans-serif;
}

.chart-wrapper {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin: 0 auto;
}

.content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  margin: 0;
  user-select: none;
}


.nav-header-container {
  width: 100%;
}

@media (max-width: 768px) {
  .chart-wrapper {
    width: 100%;
  }
}

.card {
  width: 60vw;
  height: 60vh;
  padding: 1.5rem;
  margin: 0.5rem;
  border-radius: 16px !important;
  background-color: #ffffff;
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease-in-out;
  border: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  overflow: auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #dbeafe;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1d4ed8;
  letter-spacing: 0.01em;
}

.card-badge {
  background-color: #dbeafe;
  color: #2563eb;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  letter-spacing: 0.02em;
}

.card-child {
  padding: 0.75rem 0;
  display: flex;
  flex-direction: column;
  height: calc(100% - 70px);
  overflow: hidden;
}

.card-float:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(37, 99, 235, 0.1);
  border-color: #3b82f6;
}

.search-container {
  margin-bottom: 1rem;
  padding: 0.75rem;
  background-color: #f8fafc;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
  flex-shrink: 0;
}

.table-container {
  margin-top: 0.5rem;
  width: 100%;
  overflow-x: auto;
  flex: 1;
  min-height: 0;
  position: relative;
}

.custom-table {
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  font-size: 0.95rem;
  max-height: calc(100% - 10px);
}

.custom-table th {
  font-weight: 600;
  font-size: 1rem;
  color: #1e293b;
  background-color: #f8fafc;
}

.custom-table td {
  color: #334155;
}

.avatar-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 2px solid #dbeafe;
  transition: all 0.2s ease;
}

.user-avatar:hover {
  transform: scale(1.1);
  border-color: #2563eb;
}

.edit-button {
  border-radius: 8px;
  padding: 5px 14px;
  background-color: #2563eb !important;
  border-color: #2563eb !important;
  color: white !important;
  transition: all 0.3s ease;
  font-size: 0.95rem;
  font-weight: 500;
  letter-spacing: 0.02em;
}

.edit-button:hover {
  background-color: #1d4ed8 !important;
  box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3);
  transform: translateY(-2px);
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 1rem;
  flex-shrink: 0;
  padding: 0.5rem 0;
}

.custom-dialog {
  border-radius: 16px;
  overflow: hidden;
}

.custom-dialog .el-dialog__header {
  background-color: #f8fafc;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #dbeafe;
}

.custom-dialog .el-dialog__title {
  color: #1d4ed8;
  font-weight: 600;
  font-size: 1.2rem;
  letter-spacing: 0.01em;
}

.custom-dialog .el-dialog__body {
  padding: 1.5rem;
}

.user-form .el-form-item__label {
  font-weight: 500;
  color: #475569;
  font-size: 1rem;
}

.user-form .el-input__inner {
  border-radius: 8px;
  font-size: 1rem;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 1rem;
}

.dialog-footer .el-button {
  border-radius: 8px;
  padding: 8px 20px;
  font-size: 1rem;
  font-weight: 500;
}

.dialog-footer .el-button--primary {
  background-color: #2563eb !important;
  border-color: #2563eb !important;
}

.dialog-footer .el-button--primary:hover {
  background-color: #1d4ed8 !important;
  box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3);
}

/* 响应式调整 */
@media (max-width: 1200px) {
  .card {
    width: 80vw;
  }

  .custom-table .el-table-column--mini {
    padding: 8px 0;
  }

  .edit-button {
    padding: 4px 10px;
    font-size: 0.9rem;
  }

  .el-table-column--action {
    width: 80px !important;
  }
}

@media (max-width: 768px) {
  .card {
    width: 95vw;
    padding: 1rem;
  }

  .search-container {
    padding: 0.75rem;
  }

  .el-form--inline .el-form-item {
    margin-right: 0;
    width: 100%;
  }

  .edit-button {
    padding: 3px 8px;
    font-size: 0.85rem;
  }

  .el-table-column--id {
    width: 70px !important;
  }

  .el-table-column--avatar {
    width: 70px !important;
  }

  .el-table-column--username {
    width: 120px !important;
  }

  .el-table-column--action {
    width: 70px !important;
  }
}

/* 大屏幕字体放大 (1800px+) */
@media (min-width: 1800px) {
  .card-title {
    font-size: 1.5rem;
  }

  .card-badge {
    font-size: 0.95rem;
    padding: 0.3rem 0.85rem;
  }

  .el-table {
    font-size: 1.15rem;
  }

  .el-table th {
    font-size: 1.2rem;
  }

  .pagination-container {
    padding: 0.75rem 0;
  }

  .edit-button {
    font-size: 1.1rem;
    padding: 6px 16px;
  }

  .search-container .el-input {
    font-size: 1.15rem;
  }

  .search-container .el-button {
    font-size: 1.15rem;
    padding: 10px 22px;
  }

  .custom-dialog .el-dialog__title {
    font-size: 1.4rem;
  }

  .user-form .el-form-item__label {
    font-size: 1.2rem;
  }

  .user-form .el-input {
    font-size: 1.2rem;
  }

  .dialog-footer .el-button {
    font-size: 1.2rem;
    padding: 10px 24px;
  }

  .card-child {
    padding: 1rem 0;
  }

  .search-container {
    padding: 1rem 1.25rem;
    margin-bottom: 1.25rem;
  }

  .user-avatar {
    width: 48px;
    height: 48px;
  }

  .custom-table .cell {
    padding: 10px 12px;
  }

  .el-table-column--id {
    width: 120px !important;
  }

  .el-table-column--avatar {
    width: 120px !important;
  }

  .el-table-column--username {
    width: 220px !important;
  }

  .el-table-column--action {
    width: 120px !important;
  }
}

/* 超大屏幕进放大 */
@media (min-width: 2400px) {
  .card-title {
    font-size: 1.8rem;
  }

  .card-badge {
    font-size: 1.2rem;
    padding: 0.4rem 1rem;
  }

  .el-table {
    font-size: 1.4rem;
  }

  .el-table th {
    font-size: 1.5rem;
  }

  .pagination-container {
    padding: 1rem 0;
  }

  .edit-button {
    font-size: 1.35rem;
    padding: 8px 20px;
  }

  .search-container .el-input {
    font-size: 1.4rem;
  }

  .search-container .el-button {
    font-size: 1.4rem;
    padding: 12px 26px;
  }

  .custom-dialog .el-dialog__title {
    font-size: 1.8rem;
  }

  .user-form .el-form-item__label {
    font-size: 1.5rem;
  }

  .user-form .el-input {
    font-size: 1.5rem;
  }

  .dialog-footer .el-button {
    font-size: 1.5rem;
    padding: 12px 28px;
  }

  .card-child {
    padding: 1.25rem 0;
  }

  .search-container {
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.5rem;
  }

  .user-avatar {
    width: 58px;
    height: 58px;
  }

  .custom-table .cell {
    padding: 12px 16px;
  }

  .el-table-column--id {
    width: 150px !important;
  }

  .el-table-column--avatar {
    width: 150px !important;
  }

  .el-table-column--username {
    width: 250px !important;
  }

  .el-table-column--action {
    width: 150px !important;
  }
}
</style>
