package rean_it.com.thymeleaf_springboot_tutorial.controller;

import java.util.List;

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
    public String messageExpression() {
        return "message-expression";
    }

    @GetMapping("/link-expression")
    public String linkExpression(Model model) {
        model.addAttribute("id", "22");
        return "link-expression";
    }

    @GetMapping("/fragment-expression")
    public String fragmentExpression() {
        return "fragment-expression";
    }

    @GetMapping("/users")
    public String listUsers(Model model) {
        User admin = new User("admin", "admin   admin.hkimhab@gmail.com", "ADMIN", "Male");
        User hkimhab = new User("HKimhab", "hkimhab@gmail.com", "USER", "Male");
        User guest = new User("guest", "guest   guest.hkimhab@gmail .com", "GUEST", "   Male");

        List<User> users = List.of(admin, hkimhab, guest);
        model.addAttribute("users", users);

        return "users";
    }

}
