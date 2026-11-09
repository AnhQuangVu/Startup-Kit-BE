package com.startupkit.platform.validator;

import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;

import java.lang.reflect.Field;

public class PasswordMatchValidator implements ConstraintValidator<PasswordMatch, Object> {

    @Override
    public boolean isValid(Object obj, ConstraintValidatorContext context) {
        if (obj == null) return true;

        try {
            String password = getFieldValue(obj, "password");
            String confirmPassword = getFieldValue(obj, "confirmPassword");

            if (password == null || confirmPassword == null) {
                return false;
            }

            return password.equals(confirmPassword);
        } catch (Exception e) {
            return false;
        }
    }

    private String getFieldValue(Object obj, String fieldName) throws Exception {
        Field field = obj.getClass().getDeclaredField(fieldName);
        field.setAccessible(true);
        return (String) field.get(obj);
    }
}