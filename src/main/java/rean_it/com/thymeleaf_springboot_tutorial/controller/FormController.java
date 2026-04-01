package rean_it.com.thymeleaf_springboot_tutorial.controller;

import java.util.Arrays;
import java.util.List;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

import rean_it.com.thymeleaf_springboot_tutorial.model.UserForm;

@Controller
public class FormController {

    @GetMapping("register")
    public String userRegistrationPage(Model model) {
        UserForm userForm = new UserForm();
        model.addAttribute("userForm", userForm);

        List<String> listOfProfessions = Arrays.asList("Developer", "Designer", "Manager", "Tester");
        model.addAttribute("professions", listOfProfessions);

        return "register-form";

    }
}
