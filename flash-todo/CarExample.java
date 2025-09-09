public class Car {
    private String color;
    private int wheels;
    private boolean electric;
    
    // 构造函数
    public Car(String color, int wheels, boolean electric) {
        this.color = color;
        this.wheels = wheels;
        this.electric = electric;
    }
    
    // Getter方法
    public String getColor() {
        return color;
    }
    
    public int getWheels() {
        return wheels;
    }
    
    public boolean isElectric() {
        return electric;
    }
    
    // Setter方法
    public void setColor(String color) {
        this.color = color;
    }
    
    public void setWheels(int wheels) {
        this.wheels = wheels;
    }
    
    public void setElectric(boolean electric) {
        this.electric = electric;
    }
    
    @Override
    public String toString() {
        return "Car{" +
                "color='" + color + '\'' +
                ", wheels=" + wheels +
                ", electric=" + electric +
                '}';
    }
}

class CarExample {
    public static void main(String[] args) {
        // 创建Car对象实例
        Car car = new Car("red", 4, true);
        
        // 打印Car信息
        System.out.println("Car created: " + car);
        System.out.println("Color: " + car.getColor());
        System.out.println("Wheels: " + car.getWheels());
        System.out.println("Electric: " + car.isElectric());
    }
} 