package com.startupkit.platform.service;

import jakarta.mail.MessagingException;
import jakarta.mail.internet.MimeMessage;
import lombok.AccessLevel;
import lombok.RequiredArgsConstructor;
import lombok.experimental.FieldDefaults;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
public class EmailService {

    JavaMailSender javaMailSender;
    // gửi link reset password
    public void sendLinkResetPassword (String email , String token){
        String link = "http://localhost:3000/reset-password?token=" + token;

        try {
            MimeMessage mimeMessage = javaMailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(mimeMessage, "utf-8");

            helper.setTo(email);
            helper.setSubject("Yêu cầu đặt lại mật khẩu - StartupKit");

            // Nội dung HTML cho email
            String htmlContent = String.format(
                    "<h3>Chào bạn,</h3>" +
                            "<p>Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản của bạn.</p>" +
                            "<p>Vui lòng click vào nút bên dưới để tiến hành thay đổi:</p>" +
                            "<a href='%s' style='background-color: #1976d2; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;'>Đặt lại mật khẩu</a>" +
                            "<p>Link này sẽ hết hạn sau 15 phút.</p>", link);

            helper.setText(htmlContent, true);
            javaMailSender.send(mimeMessage);

        } catch (MessagingException e) {
            throw new RuntimeException("Lỗi gửi email: " + e.getMessage());
        }
    }
}
