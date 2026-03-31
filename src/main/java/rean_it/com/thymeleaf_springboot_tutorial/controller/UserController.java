package rean_it.com.thymeleaf_springboot_tutorial.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

import rean_it.com.thymeleaf_springboot_tutorial.model.User;

@Controller
public class UserController {

    @GetMapping("/user-variable-expression")
    public String userVariableExpression(Model model) {
        User user = new User("HKimhab", "hkimhab@gmail.com", "ADMIN", "Male");
        model.addAttribute("user", user);

        // Return the name of the Thymeleaf template to be rendered
        // In this case, it will look for a template named
        // "user-variable-expression.html"
        return "user-variable-expression";
    }

    @GetMapping("/user-selection-expression")
    public String userSelectionExpression(Model model) {
        User user = new User("HKimhab", "hkimhab@gmail.com", "ADMIN", "Male");
        model.addAttribute("user", user);

        return "user-selection-expression";
    }

    @GetMapping("/message-expression")
    public String messageExpression(Model model) {
        return "message-expression";
    }

}
