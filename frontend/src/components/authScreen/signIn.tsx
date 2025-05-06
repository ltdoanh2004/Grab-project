import React from "react";
import { Form, Input, Button, Typography, Card, message, Alert } from "antd";
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
  const [error, setError] = React.useState<string | null>(null);

  const handleFinish = async (values: any) => {
    setError(null);
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
      console.error("Login error:", err);

      let errorMessage = "Tên đăng nhập hoặc mật khẩu không đúng!";

      if (err?.response?.data?.message) {
        const message = err.response.data.message;
        if (message.includes("record not found")) {
          errorMessage =
            "Tài khoản không tồn tại. Vui lòng kiểm tra lại hoặc đăng ký mới.";
        } else {
          errorMessage = message;
        }
      } else if (err?.message) {
        errorMessage = err.message;
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
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

        {error && (
          <Alert
            message={error}
            type="error"
            showIcon
            closable
            className="mb-4"
            onClose={() => setError(null)}
          />
        )}

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
            <Input
              prefix={<UserOutlined />}
              placeholder="Tên đăng nhập hoặc email"
              size="large"
            />
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
              disabled={loading}
            >
              {loading ? "Đang đăng nhập..." : "Đăng nhập"}
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
