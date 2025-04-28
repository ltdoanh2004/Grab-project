import React from "react";
import { Form, Input, Button, Typography, Card, message } from "antd";
import { UserOutlined, MailOutlined, LockOutlined } from "@ant-design/icons";
import { register } from "../../services/travelPlanApi";

const { Title, Text } = Typography;

interface SignUpProps {
  onSwitchToSignIn?: () => void;
  onSignUpSuccess?: () => void;
}

export const SignUp: React.FC<SignUpProps> = ({
  onSwitchToSignIn,
  onSignUpSuccess,
}) => {
  const [form] = Form.useForm();

  const handleFinish = async (values: any) => {
    try {
      const res = await register(values);
      localStorage.setItem("access_token", res.data.access_token);
      message.success("Đăng ký thành công! Đã tự động đăng nhập.");
      setTimeout(() => {
        window.dispatchEvent(new Event("storage"));
        onSignUpSuccess?.();
      }, 1200);
    } catch (err: any) {
      message.error(
        err?.response?.data?.message || "Đăng ký thất bại. Vui lòng thử lại."
      );
    }
  };
  return (
    <div className="flex justify-center items-center min-h-[500px]">
      <Card className="w-full max-w-md shadow-lg rounded-2xl p-8">
        <div className="mb-6 text-center">
          <Title level={3} className="mb-1">
            Đăng ký tài khoản
          </Title>
          <Text type="secondary">
            Tạo tài khoản để bắt đầu lên kế hoạch du lịch!
          </Text>
        </div>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleFinish}
          autoComplete="off"
        >
          <Form.Item
            label="Email"
            name="email"
            rules={[
              { required: true, message: "Vui lòng nhập email!" },
              { type: "email", message: "Email không hợp lệ!" },
            ]}
          >
            <Input
              prefix={<MailOutlined />}
              placeholder="Nhập email"
              size="large"
            />
          </Form.Item>
          <div className="flex gap-2">
            <Form.Item
              label="Tên"
              name="first_name"
              className="flex-1"
              rules={[{ required: true, message: "Vui lòng nhập tên!" }]}
            >
              <Input prefix={<UserOutlined />} placeholder="Tên" size="large" />
            </Form.Item>
            <Form.Item
              label="Họ"
              name="last_name"
              className="flex-1"
              rules={[{ required: true, message: "Vui lòng nhập họ!" }]}
            >
              <Input prefix={<UserOutlined />} placeholder="Họ" size="large" />
            </Form.Item>
          </div>
          <Form.Item
            label="Tên đăng nhập"
            name="username"
            rules={[
              { required: true, message: "Vui lòng nhập tên đăng nhập!" },
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="Tên đăng nhập"
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
            >
              Đăng ký
            </Button>
          </Form.Item>
        </Form>

        <div className="text-center">
          <Text>Bạn đã có tài khoản?</Text>{" "}
          <Button type="link" onClick={onSwitchToSignIn}>
            Đăng nhập
          </Button>
        </div>
      </Card>
    </div>
  );
};
