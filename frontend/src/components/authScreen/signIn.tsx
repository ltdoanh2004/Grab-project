import React from "react";
import { Form, Input, Button, Typography, Card, message } from "antd";
import { UserOutlined, LockOutlined } from "@ant-design/icons";
import { login } from "../../services/travelPlanApi";

const { Title, Text } = Typography;

interface SignInProps {
  onSwitchToSignUp?: () => void;
  onLoginSuccess?: () => void;
}
export const SignIn: React.FC<SignInProps> = ({
  onSwitchToSignUp,
  onLoginSuccess,
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = React.useState(false);

  const handleFinish = async (values: any) => {
    setLoading(true);
    try {
      const res = await login({
        password: values.password,
        username: values.username,
      });
      localStorage.setItem("access_token", res.data.access_token);
      if (res.data.refresh_token) {
        localStorage.setItem("refresh_token", res.data.refresh_token);
      }
      message.success("Đăng nhập thành công!");
      setTimeout(() => {
        window.dispatchEvent(new Event("storage"));
        onLoginSuccess?.();
      }, 1200);
    } catch (err: any) {
      message.error(
        err?.response?.data?.message || "Đăng nhập thất bại. Vui lòng thử lại!"
      );
    }
  };

  return (
    <div className="flex justify-center items-center min-h-[500px]">
      <Card className="w-full max-w-md shadow-lg rounded-2xl p-8">
        <div className="mb-6 text-center">
          <Title level={3} className="mb-1">
            Đăng nhập
          </Title>
          <Text type="secondary">
            Chào mừng bạn quay lại! Đăng nhập để tiếp tục.
          </Text>
        </div>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleFinish}
          autoComplete="off"
        >
          <Form.Item
            label="Tên đăng nhập"
            name="username"
            rules={[
              { required: true, message: "Vui lòng nhập tên đăng nhập!" },
            ]}
          >
            <Input prefix={<UserOutlined />} placeholder="Tên" size="large" />
          </Form.Item>
          <Form.Item
            label="Mật khẩu"
            name="password"
            rules={[{ required: true, message: "Vui lòng nhập mật khẩu!" }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Nhập mật khẩu"
              size="large"
            />
          </Form.Item>
          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              className="w-full !bg-black !rounded-full"
              size="large"
              loading={loading}
            >
              Đăng nhập
            </Button>
          </Form.Item>
        </Form>

        <div className="text-center">
          <Text>Chưa có tài khoản?</Text>{" "}
          <Button type="link" onClick={onSwitchToSignUp}>
            Đăng ký
          </Button>
        </div>
      </Card>
    </div>
  );
};
